sed -i -e "s/\(^[[:space:]]*# -*.* \)---\+/\1$(printf '%.0s-' {0..99})/" "$@" 
sed -i -e "s/^\(.\{99\}\)-\+$/\1/" "$@"