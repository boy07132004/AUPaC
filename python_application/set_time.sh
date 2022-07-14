sudo timedatectl set-timezone Asia/Taipei

echo Set date and time
echo ex: 20210713
read -p 'Date?  ' _date
echo ex: 23:59
read -p 'Time?  ' _time

sudo date -s "${_date} ${_time}"
