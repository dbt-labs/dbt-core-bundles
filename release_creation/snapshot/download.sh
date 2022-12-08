set -e
# pyenv install $3 --skip-existing
base_dir=$1
install_env=".snapshot-env-$3"
rm -rf $install_env
python -m venv $install_env --system-site-packages
. $install_env/bin/activate

pyenv global $3
pyenv local $3
python -m pip install --upgrade pip --progress-bar off
python -m pip install wheel --progress-bar off

rm -rf $base_dir
mkdir  -p $base_dir

python -m pip download \
 --progress-bar off \
 --prefer-binary \
 --dest $base_dir \
 --no-cache-dir \
 $2