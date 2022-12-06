set -e
pyenv install $3 --skip-existing
pyenv virtualenv $3 snapshot-env -f
pyenv local snapshot-env
python -m pip install --upgrade pip
rm -rf $1
mkdir $1
python -m pip download \
 --dest $1 \
 $2