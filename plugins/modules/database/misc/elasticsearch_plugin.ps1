#!powershell

#AnsibleRequires -CSharpUtil Ansible.Basic

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2

$spec = @{
    options = @{
        name = @{ type = 'str'; required = $true }
        state = @{ type = 'str'; default = 'present'; choices = @( 'present', 'absent' ) }
        src = @{ type = 'str'; required = $false }
        url = @{ type = 'str'; required = $false }
        timeout = @{ type = 'str'; default = '1m' }
        force = @{ type = 'bool'; default = $false }
        plugin_bin = @{ type = 'path'; required = $false }
        plugin_dir = @{ type = 'path'; required = $false }
        proxy_host = @{ type = 'str'; required = $false }
        proxy_port = @{ type = 'str'; required = $false }
        version = @{ type = 'str'; required = $false }
    }
    #mutually_exclusive = @(( 'src', 'url' ))
    supports_check_mode = $true
}

$script:PACKAGE_STATE_MAP = @{
    present="install"
    absent="remove"
}

$script:PLUGIN_BIN_PATHS = @(
    'c:/elasticsearch/bin/elasticsearch-plugin.bat',
    $env:ES_HOME + '/bin/elasticsearch-plugin.bat'
)

$script:PLUGIN_DIR_PATHS = @(
    'c:/elasticsearch/plugins/',
    $env:ES_HOME + '/plugins/'
)

# Declaration : https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/csharp/Ansible.Basic.cs
$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$PluginName = $module.Params.name
$PluginState = $module.Params.state
$PluginSrc = $module.Params.src
$PluginUrl = $module.Params.url
$PluginTimeout = $module.Params.timeout
$PluginForce = $module.Params.force
$PluginProxyHost = $module.Params.proxy_host
$PluginProxyPort = $module.Params.proxy_port
$PluginVersion = $module.Params.version

Function Get-Plugin-Repo($name) {
    $parts = $name.Split("/")
    $repo = $parts[0]
    if ($parts.Count -gt 1) {
        $repo = $parts[1]
    }

    # remove elasticsearch- prefix
    # remove es- prefix
    foreach ($string in @("elasticsearch-", "es-")) {
        if ($repo.StartsWith($string)) {
            return $repo[${string.Count}..${repo.Count}]
        }
    }
    return $repo
}
Function Test-Plugin-Present($plugin_name, $plugin_dir) {
    return Test-Path -Path "$(Join-Path -Path "$plugin_dir" -ChildPath "$plugin_name")" -PathType "Container"
}
Function Get-Error ($msg) {
    $reason = "ERROR: "
    return $msg.Substring($($msg.IndexOf($reason) + $reason.Length), $msg.Length).Trim()
}

Function Install-Plugin ([Ansible.Basic.AnsibleModule]$module, $plugin_bin, $name, $version, $src, $url, $proxy_host, $proxy_port, $timeout, $force) {
    $cmd = $plugin_bin
    $cmd_args = @($script:PACKAGE_STATE_MAP["present"])

    $is_old_command = $(Split-Path -Path "$plugin_bin" -Leaf) -match "^plugin(\.bat)?$"
    if ($is_old_command) {
        if ($timeout) {
            $cmd_args += "--timeout $timeout"
        }
    }

    if ($proxy_host -and $proxy_port) {
        $cmd_args += "-DproxyHost=$proxy_host"
        $cmd_args += "-DproxyPort=$proxy_port"
    }

    # Legacy ES 1.x
    if ($url) {
        $cmd_args += "--url $url"
    }

    if ($force) {
        $cmd_args += "--batch"
    }
    if ($src) {
        $cmd_args += $src
    } else {
        if ($is_old_command -and $version) {
            $name = $name + '/' + $version
        }
        $cmd_args += $name
    }

    if ($module.CheckMode) {
        $rc = 0
        $out = "check mode"
        $err = ""
    } else {
        $outFile=Join-Path -Path $module.TmpDir -ChildPath "out.txt"
        $errFile=Join-Path -Path $module.TmpDir -ChildPath "err.txt"
        $process=Start-Process "$cmd" -ArgumentList $cmd_args -Wait -PassThru `
          -RedirectStandardError "$errFile" -RedirectStandardOutput "$outFile"
        $out=[string]$(Get-Content -Path "$outFile" -Raw)
        $err=[string]$(Get-Content -Path "$errFile" -Raw)
        $rc=$process.ExitCode
    }

    if ($rc -ne 0) {
        $reason = Get-Error $out
        $module.FailJson("Installing plugin '$name' failed: $reason \n $err")
    }

    return $true, $((@($cmd) + $cmd_args) -join " "), $out, $err
}
Function Remove-Plugin ([Ansible.Basic.AnsibleModule]$module, $plugin_bin, $name) {
    $cmd = $plugin_bin
    $cmd_args = @($script:PACKAGE_STATE_MAP["absent"], (Get-Plugin-Repo($plugin_name)))

    if ($module.CheckMode) {
        $rc = 0
        $out = "check mode"
        $err = ""
    } else {
        $outFile=Join-Path -Path $module.TmpDir -ChildPath "out.txt"
        $errFile=Join-Path -Path $module.TmpDir -ChildPath "err.txt"
        $process=Start-Process "$cmd" -ArgumentList $cmd_args -Wait -PassThru `
          -RedirectStandardError "$errFile" -RedirectStandardOutput "$outFile"
        $out=[string]$(Get-Content -Path "$outFile" -Raw)
        $err=[string]$(Get-Content -Path "$errFile" -Raw)
        $rc=$process.ExitCode
    }

    if ($rc -ne 0) {
        $reason = Get-Error($out)
        $module.FailJson("Removing plugin '$plugin_name' failed: $reason \n $err")
    }

    return $true, $((@($cmd) + $cmd_args) -join " "), $out, $err
}

Function Get-Plugin-Bin ([Ansible.Basic.AnsibleModule]$module) {
    $valid_plugin_bin=$null
    if (-Not [string]::IsNullOrEmpty($module.Params.plugin_bin) -and (Test-Path -Path "$($module.Params.plugin_bin)" -PathType "Leaf")) {
        $valid_plugin_bin = $module.Params.plugin_bin
    } else {
        foreach ($path in $script:PLUGIN_BIN_PATHS) {
            if (Test-Path -Path "$path" -PathType "Leaf") {
                $valid_plugin_bin = $path
                break
            }
        }
    }
    if ([string]::IsNullOrEmpty($valid_plugin_bin)) {
        $module.FailJson("$($module.Params.plugin_bin) does not exist and no other valid plugin installers were found. Make sure Elasticsearch is installed.")
    }

    return $valid_plugin_bin
}

Function Get-Plugin-Dir ([Ansible.Basic.AnsibleModule]$module) {
    $valid_plugin_dir=$null
    if (-Not [string]::IsNullOrEmpty($module.Params.plugin_dir) -and (Test-Path -Path "$($module.Params.plugin_dir)" -PathType "Container")) {
        $valid_plugin_dir = $module.Params.plugin_dir
    } else {
        foreach ($path in $script:PLUGIN_DIR_PATHS) {
            if (Test-Path -Path "$path" -PathType "Container") {
                $valid_plugin_dir = $path
                break
            }
        }
    }
    if ([string]::IsNullOrEmpty($valid_plugin_dir)) {
        $module.FailJson("$($module.Params.plugin_dir) does not exist and no other valid plugin dir were found. Make sure Elasticsearch is installed.")
    }

    return $valid_plugin_dir
}

$changed = $false
$PluginBin = Get-Plugin-Bin $module

$repo = Get-Plugin-Repo $PluginName
$PluginDir = Get-Plugin-Dir $module
$present = Test-Plugin-Present $repo $PluginDir

# skip if the state is correct
if (($present -and $PluginState -eq "present") -or ($PluginState -eq "absent" -and -not $present)) {
    $module.Result.name = $PluginName
    $module.Result.state = $PluginState
    $module.ExitJson()
}

if ($PluginState -eq "present") {
    $changed, $command, $out, $err = Install-Plugin $module $PluginBin $PluginName $PluginVersion $PluginSrc $PluginUrl $PluginProxyHost $PluginProxyPort $PluginTimeout $PluginForce
} elseif ($PluginState -eq "absent") {
    $changed, $command, $out, $err = Remove-Plugin $module $PluginBin $PluginName
}
if ($changed) {
    $changed = $changed
    $module.Result.cmd = $command
    $module.Result.stdout = $out
    $module.Result.stderr = $err
}

$module.Result.name = $PluginName
$module.Result.timeout = $PluginTimeout
$module.Result.url = $PluginUrl
$module.Result.state = $PluginState
$module.Result.changed = $changed
$module.ExitJson()
