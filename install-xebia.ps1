$resetwifi = Read-Host "Reset wifi (y/n)?"

$appsourcedir = "C:\Users\FokkoVeegens\Repos\gh-Badger\home\badge\apps\xebia"
$apptargetdir = "D:\apps\xebia"

$menusourcefile = "C:\Users\FokkoVeegens\Repos\gh-Badger\home\badge\apps\menu\__init__device.py"
$menutargetfile = "D:\apps\menu\__init__.py"

$sketchfolder = "D:\apps\sketch"

$secretssourcefile = "C:\Users\FokkoVeegens\Repos\gh-Badger\home\badge\secrets_empty.py"
$secretstargetfile = "D:\secrets.py"

$appfiles = @(
    "__init__.py",
    "icon.png",
    "xebia-logo.png",
    "block_positions.json"
)

if (!(Test-Path -Path $apptargetdir)) {
    New-Item -ItemType Directory -Path $apptargetdir
}

foreach ($file in $appfiles) {
    $source = Join-Path -Path $appsourcedir -ChildPath $file
    $destination = Join-Path -Path $apptargetdir -ChildPath $file
    Copy-Item -Path $source -Destination $destination -Force
}

Copy-Item -Path $menusourcefile -Destination $menutargetfile -Force

Remove-Item -Path $sketchfolder -Recurse -Force -ErrorAction SilentlyContinue

if ($resetwifi -eq "y") {
    Copy-Item -Path $secretssourcefile -Destination $secretstargetfile -Force
}