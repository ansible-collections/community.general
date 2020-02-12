#!powershell

# Copyright: (c) 2015, Sam Liu <sam.liu@activenetwork.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#Requires -Module Ansible.ModuleUtils.Legacy

$params = Parse-Args $args -supports_check_mode $true

$result = @{
    win_file_version = @{}
    changed = $false
}

$path = Get-AnsibleParam -obj $params -name "path" -type "path" -failifempty $true -resultobj $result

If (-Not (Test-Path -Path $path -PathType Leaf)){
    Fail-Json $result "Specified path $path does not exist or is not a file."
}
$ext = [System.IO.Path]::GetExtension($path)
If ( $ext -notin '.exe', '.dll'){
    Fail-Json $result "Specified path $path is not a valid file type; must be DLL or EXE."
}

Try {
    $_version_fields = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($path)
    $file_version = $_version_fields.FileVersion
    If ($null -eq $file_version){
        $file_version = ''
    }
    $product_version = $_version_fields.ProductVersion
    If ($null -eq $product_version){
        $product_version= ''
    }
    $file_major_part = $_version_fields.FileMajorPart
    If ($null -eq $file_major_part){
        $file_major_part= ''
    }
    $file_minor_part = $_version_fields.FileMinorPart
    If ($null -eq $file_minor_part){
        $file_minor_part= ''
    }
    $file_build_part = $_version_fields.FileBuildPart
    If ($null -eq $file_build_part){
        $file_build_part = ''
    }
    $file_private_part = $_version_fields.FilePrivatePart
    If ($null -eq $file_private_part){
        $file_private_part = ''
    }
}
Catch{
    Fail-Json $result "Error: $_.Exception.Message"
}

$result.win_file_version.path = $path.toString()
$result.win_file_version.file_version = $file_version.toString()
$result.win_file_version.product_version = $product_version.toString()
$result.win_file_version.file_major_part = $file_major_part.toString()
$result.win_file_version.file_minor_part = $file_minor_part.toString()
$result.win_file_version.file_build_part = $file_build_part.toString()
$result.win_file_version.file_private_part = $file_private_part.toString()
Exit-Json $result;
