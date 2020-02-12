#!powershell

# Copyright: (c) 2015, Hans-Joachim Kliemeck <git@kliemeck.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#Requires -Module Ansible.ModuleUtils.Legacy
#Requires -Module Ansible.ModuleUtils.SID

#Functions
Function NormalizeAccounts {
    param(
        [parameter(valuefrompipeline=$true)]
        $users
    )

    $users = $users.Trim()
    If ($users -eq "") {
        $splitUsers = [Collections.Generic.List[String]] @()
    }
    Else {
        $splitUsers = [Collections.Generic.List[String]] $users.Split(",")
    }

    $normalizedUsers = [Collections.Generic.List[String]] @()
    ForEach($splitUser in $splitUsers) {
        $sid = Convert-ToSID -account_name $splitUser
        if (!$sid) {
            Fail-Json $result "$splitUser is not a valid user or group on the host machine or domain"
        }

        $normalizedUser = (New-Object System.Security.Principal.SecurityIdentifier($sid)).Translate([System.Security.Principal.NTAccount])
        $normalizedUsers.Add($normalizedUser)
    }

    return ,$normalizedUsers
}

$result = @{
    changed = $false
    actions = @() # More for debug purposes
}

$params = Parse-Args $args -supports_check_mode $true

# While the -SmbShare cmdlets have a -WhatIf parameter, they don't honor it, need to skip the cmdlet if in check mode
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false

$name = Get-AnsibleParam -obj $params -name "name" -type "str" -failifempty $true
$state = Get-AnsibleParam -obj $params -name "state" -type "str" -default "present" -validateset "present","absent"
$rule_action  = Get-AnsibleParam -obj $params -name "rule_action" -type "str" -default "set" -validateset "set","add"

if (-not (Get-Command -Name Get-SmbShare -ErrorAction SilentlyContinue)) {
    Fail-Json $result "The current host does not support the -SmbShare cmdlets required by this module. Please run on Server 2012 or Windows 8 and later"
}

$share = Get-SmbShare -Name $name -ErrorAction SilentlyContinue
If ($state -eq "absent") {
    If ($share) {
        # See message around -WhatIf where $check_mode is defined
        if (-not $check_mode) {
            Remove-SmbShare -Force -Name $name | Out-Null
        }
        $result.actions += "Remove-SmbShare -Force -Name $name"
        $result.changed = $true
    }
} Else {
    $path = Get-AnsibleParam -obj $params -name "path" -type "path" -failifempty $true
    $description = Get-AnsibleParam -obj $params -name "description" -type "str" -default ""

    $permissionList = Get-AnsibleParam -obj $params -name "list" -type "bool" -default $false
    $folderEnum = if ($permissionList) { "Unrestricted" } else { "AccessBased" }

    $permissionRead = Get-AnsibleParam -obj $params -name "read" -type "str" -default "" | NormalizeAccounts
    $permissionChange = Get-AnsibleParam -obj $params -name "change" -type "str" -default "" | NormalizeAccounts
    $permissionFull = Get-AnsibleParam -obj $params -name "full" -type "str" -default "" | NormalizeAccounts
    $permissionDeny = Get-AnsibleParam -obj $params -name "deny" -type "str" -default "" | NormalizeAccounts

    $cachingMode = Get-AnsibleParam -obj $params -name "caching_mode" -type "str" -default "Manual" -validateSet "BranchCache","Documents","Manual","None","Programs","Unknown"
    $encrypt = Get-AnsibleParam -obj $params -name "encrypt" -type "bool" -default $false

    If (-Not (Test-Path -Path $path)) {
        Fail-Json $result "$path directory does not exist on the host"
    }

    # normalize path and remove slash at the end
    $path = (Get-Item $path).FullName -replace "\\$"

    # need to (re-)create share
    If (-not $share) {
        if (-not $check_mode) {
            New-SmbShare -Name $name -Path $path | Out-Null
        }
        $share = Get-SmbShare -Name $name -ErrorAction SilentlyContinue

        $result.changed = $true
        $result.actions += "New-SmbShare -Name $name -Path $path"
        # if in check mode we cannot run the below as no share exists so just
        # exit early
        if ($check_mode) {
            Exit-Json -obj $result
        }
    }
    If ($share.Path -ne $path) {
        if (-not $check_mode) {
            Remove-SmbShare -Force -Name $name | Out-Null
            New-SmbShare -Name $name -Path $path | Out-Null
        }
        $share = Get-SmbShare -Name $name -ErrorAction SilentlyContinue
        $result.changed = $true
        $result.actions += "Remove-SmbShare -Force -Name $name"
        $result.actions += "New-SmbShare -Name $name -Path $path"
    }

    # updates
    If ($share.Description -ne $description) {
        if (-not $check_mode) {
            Set-SmbShare -Force -Name $name -Description $description | Out-Null
        }
        $result.changed = $true
        $result.actions += "Set-SmbShare -Force -Name $name -Description $description"
    }
    If ($share.FolderEnumerationMode -ne $folderEnum) {
        if (-not $check_mode) {
            Set-SmbShare -Force -Name $name -FolderEnumerationMode $folderEnum | Out-Null
        }
        $result.changed = $true
        $result.actions += "Set-SmbShare -Force -Name $name -FolderEnumerationMode $folderEnum"
    }
    if ($share.CachingMode -ne $cachingMode) {
        if (-not $check_mode) {
            Set-SmbShare -Force -Name $name -CachingMode $cachingMode | Out-Null
        }
        $result.changed = $true
        $result.actions += "Set-SmbShare -Force -Name $name -CachingMode $cachingMode"
    }
    if ($share.EncryptData -ne $encrypt) {
        if (-not $check_mode) {
            Set-SmbShare -Force -Name $name -EncryptData $encrypt | Out-Null
        }
        $result.changed = $true
        $result.actions += "Set-SmbShare -Force -Name $name -EncryptData $encrypt"
    }

    # clean permissions that imply others
    ForEach ($user in $permissionFull) {
        $permissionChange.remove($user) | Out-Null
        $permissionRead.remove($user) | Out-Null
    }
    ForEach ($user in $permissionChange) {
        $permissionRead.remove($user) | Out-Null
    }

    # remove permissions
    $permissions = Get-SmbShareAccess -Name $name
    if($rule_action -eq "set") {
        ForEach ($permission in $permissions) {
            If ($permission.AccessControlType -eq "Deny") {
                $cim_count = 0
                foreach ($count in $permissions) {
                    $cim_count++
                }
                # Don't remove the Deny entry for Everyone if there are no other permissions set (cim_count == 1)
                if (-not ($permission.AccountName -eq 'Everyone' -and $cim_count -eq 1)) {
                    If (-not ($permissionDeny.Contains($permission.AccountName))) {
                        if (-not $check_mode) {
                            Unblock-SmbShareAccess -Force -Name $name -AccountName $permission.AccountName | Out-Null
                        }
                        $result.changed = $true
                        $result.actions += "Unblock-SmbShareAccess -Force -Name $name -AccountName $($permission.AccountName)"
                    } else {
                        # Remove from the deny list as it already has the permissions
                        $permissionDeny.remove($permission.AccountName) | Out-Null
                    }
                }
            } ElseIf ($permission.AccessControlType -eq "Allow") {
                If ($permission.AccessRight -eq "Full") {
                    If (-not ($permissionFull.Contains($permission.AccountName))) {
                        if (-not $check_mode) {
                            Revoke-SmbShareAccess -Force -Name $name -AccountName $permission.AccountName | Out-Null
                        }
                        $result.changed = $true
                        $result.actions += "Revoke-SmbShareAccess -Force -Name $name -AccountName $($permission.AccountName)"

                        Continue
                    }

                    # user got requested permissions
                    $permissionFull.remove($permission.AccountName) | Out-Null
                } ElseIf ($permission.AccessRight -eq "Change") {
                    If (-not ($permissionChange.Contains($permission.AccountName))) {
                        if (-not $check_mode) {
                            Revoke-SmbShareAccess -Force -Name $name -AccountName $permission.AccountName | Out-Null
                        }
                        $result.changed = $true
                        $result.actions += "Revoke-SmbShareAccess -Force -Name $name -AccountName $($permission.AccountName)"

                        Continue
                    }

                    # user got requested permissions
                    $permissionChange.remove($permission.AccountName) | Out-Null
                } ElseIf ($permission.AccessRight -eq "Read") {
                    If (-not ($permissionRead.Contains($permission.AccountName))) {
                        if (-not $check_mode) {
                            Revoke-SmbShareAccess -Force -Name $name -AccountName $permission.AccountName | Out-Null
                        }
                        $result.changed = $true
                        $result.actions += "Revoke-SmbShareAccess -Force -Name $name -AccountName $($permission.AccountName)"

                        Continue
                    }

                    # user got requested permissions
                    $permissionRead.Remove($permission.AccountName) | Out-Null
                }
            }
        }
    } ElseIf ($rule_action -eq "add") {
        ForEach($permission in $permissions) {
            If ($permission.AccessControlType -eq "Deny") {
                If ($permissionDeny.Contains($permission.AccountName)) {
                    $permissionDeny.Remove($permission.AccountName)
                }
            } ElseIf ($permission.AccessControlType -eq "Allow") {
                If ($permissionFull.Contains($permission.AccountName) -and $permission.AccessRight -eq "Full") {
                    $permissionFull.Remove($permission.AccountName)
                } ElseIf ($permissionChange.Contains($permission.AccountName) -and $permission.AccessRight -eq "Change") {
                    $permissionChange.Remove($permission.AccountName)
                } ElseIf ($permissionRead.Contains($permission.AccountName) -and $permission.AccessRight -eq "Read") {
                    $permissionRead.Remove($permission.AccountName)
                }
            }
        }
    }

    # add missing permissions
    ForEach ($user in $permissionRead) {
        if (-not $check_mode) {
            Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight "Read" | Out-Null
        }
        $result.changed = $true
        $result.actions += "Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight Read"
    }
    ForEach ($user in $permissionChange) {
        if (-not $check_mode) {
            Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight "Change" | Out-Null
        }
        $result.changed = $true
        $result.actions += "Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight Change"
    }
    ForEach ($user in $permissionFull) {
        if (-not $check_mode) {
            Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight "Full" | Out-Null
        }
        $result.changed = $true
        $result.actions += "Grant-SmbShareAccess -Force -Name $name -AccountName $user -AccessRight Full"
    }
    ForEach ($user in $permissionDeny) {
        if (-not $check_mode) {
            Block-SmbShareAccess -Force -Name $name -AccountName $user | Out-Null
        }
        $result.changed = $true
        $result.actions += "Block-SmbShareAccess -Force -Name $name -AccountName $user"
    }
}

Exit-Json $result
