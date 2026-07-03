# package_project.ps1
# Script para compilar el entregable final de la evaluación técnica ETISEJr_JairMolina.zip
# Sistema de Extracción de Aire Caliente - Jaguar de México
# Candidato: Ing. Jair Molina Arce

$ZipName = "ETISEJr_JairMolina.zip"
$TempDir = Join-Path $PSScriptRoot "temp_archive"

# Limpieza previa
if (Test-Path $ZipName) {
    Remove-Item $ZipName -Force
}
if (Test-Path $TempDir) {
    Remove-Item $TempDir -Recurse -Force
}

# Crear directorio temporal
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Copiar archivos individuales del root
Copy-Item (Join-Path $PSScriptRoot "ETISEJr_JairMolina.md") -Destination $TempDir
Copy-Item (Join-Path $PSScriptRoot "README.md") -Destination $TempDir

# Función para copiar carpetas recursivamente excluyendo archivos no deseados
function Copy-FilteredFolder($Source, $Dest) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
    
    Get-ChildItem -Path $Source -Recurse | ForEach-Object {
        $RelativePath = $_.FullName.Substring($Source.Length + 1)
        $TargetFile = Join-Path $Dest $RelativePath
        
        if ($_.PSIsContainer) {
            # Es un directorio, crear si no existe
            New-Item -ItemType Directory -Path $TargetFile -Force | Out-Null
        } else {
            # Es un archivo, verificar exclusiones
            $FileName = $_.Name
            
            # Excluir *.bak, *.kicad_prl, *~ y carpetas de caché
            if ($FileName -like "*.bak" -or $FileName -like "*.kicad_prl" -or $FileName -like "*~" -or $_.FullName -like "*__pycache__*") {
                Write-Host "Excluyendo: $RelativePath" -ForegroundColor Yellow
            } else {
                # Asegurar que el directorio padre existe antes de copiar el archivo
                $ParentDir = Split-Path $TargetFile -Parent
                if (-not (Test-Path $ParentDir)) {
                    New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
                }
                Copy-Item $_.FullName -Destination $TargetFile -Force
            }
        }
    }
}

# Copiar carpetas filtradas
Copy-FilteredFolder (Join-Path $PSScriptRoot "firmware") (Join-Path $TempDir "firmware")
Copy-FilteredFolder (Join-Path $PSScriptRoot "kicad") (Join-Path $TempDir "kicad")

# Crear el archivo ZIP a partir del contenido temporal
Write-Host "Comprimiendo entregable en $ZipName..." -ForegroundColor Green
Compress-Archive -Path "$TempDir\*" -DestinationPath (Join-Path $PSScriptRoot $ZipName) -Force

# Limpiar directorio temporal
Remove-Item $TempDir -Recurse -Force

Write-Host "¡Entregable creado exitosamente como $ZipName!" -ForegroundColor Green
