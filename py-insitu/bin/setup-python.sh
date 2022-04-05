#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
BIN=$(dirname "$SCRIPT")

# shellcheck source=./paths.sh
. "$BIN/paths.sh"

if [ ! -d "$INSTALL_TMPD" ]; then
    mkdir "$INSTALL_TMPD"
fi

cd "$INSTALL_TMPD" || exit

if [ ! -f "$PYTGZ" ]; then
    wget "$PYSRC_URL"
fi
if [ ! -f "$PYTGZ" ]; then
    echo "Could not download Python from $PYSRC_URL"
    exit
fi

if [ ! -d "$PYSRC" ]; then
    echo "Unpacking $PYTGZ => $PYSRC"
    tar -zxf "$PYTGZ"
fi

if [ ! -d "$PYSRC" ]; then
    echo "Error unpacking $PYSRC"
    exit
fi

cd "$PYSRC" || exit

echo "Deleting old python install $PYTHOND"
rm -rf "$PYTHOND"
mkdir -p "$PYTHOND"

echo "Deleting python envs $PYENVS/*"

rm -rf "$PYENVS"
mkdir -p "$PYENVS"

./configure --prefix="$PYTHOND" --enable-optimizations --with-lto --enable-loadable-sqlite-extensions

make clean
make build_all
make install

cd "$ROOTD" || exit

"$PYTHOND/bin/pip3" install --ignore-installed virtualenv
"$PYTHOND/bin/virtualenv" "$S2AND_ENV"

echo "Done. Activate with 'source $S2AND_ENV/bin/activate'"
