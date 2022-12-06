set -e
# pyenv install $3 --skip-existing
install_env=".snapshot-env-$3"
pyenv local $3
python -mvenv $install_env --system-site-packages
. $install_env/bin/activate
python -m pip install --upgrade pip
python -m pip install wheel
rm -rf $1
mkdir  -p $1
python -m pip download \
 --dest $1 \
 $2