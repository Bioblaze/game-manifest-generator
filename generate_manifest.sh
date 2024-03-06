#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Ensure required envs are set
: ${version:?}
: ${output_file:?}
: ${output_folder:?}
: ${input_folder:?}

OutputDir=$(pwd)/${output_folder:-.}

echo "#################################"
echo "#        Building Manifest      #"
echo "#################################"

python /root/manifest_creator.py --t 3 --output_folder $OutputDir  --dir ${input_folder} --export ${output_file} --build ${version}