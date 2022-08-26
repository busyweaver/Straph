
if [[ $# -ne 2 ]]; then
    echo "Bad syntax."
    echo "Usage: $0 basename nb_points"
    exit
fi

export PYTHONPATH="${PYTHONPATH}:../Lib/"

python2 ../betweenness_all.py "$1".ls $2 > "$1".val

python2 visu.py "$1" > "$1".py

python2 "$1".py | grep . > "$1".fig; fig2dev -L eps < "$1".fig > "$1".eps

# cat ex.ls | awk 'function min(a, b) { return a < b ? a: b }{if (NF==4) print $1,min(45,$2+3),$3,$4; else print $0;}' > ex-dur.ls 
