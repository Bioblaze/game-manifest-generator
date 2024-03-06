#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Ensure required envs are set
: ${version:?}
: ${output_file:?}
: ${output_folder:?}
: ${input_folder:?}

OutputDir=$(pwd)/${output_folder:-.}
InputDir=$(pwd)/${input_folder:-.}

echo "#################################"
echo "#        Building Manifest      #"
echo "#################################"

echo "Exporting to: ${OutputDir}"
echo "Exporting as: ${output_file}"
echo "Generating for Folder: ${InputDir}"

python /root/manifest_creator.py --t 4 --output_folder $OutputDir  --directory ${InputDir} --export ${output_file} --build ${version}