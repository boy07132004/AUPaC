sudo timedatectl set-timezone Asia/Taipei

echo Set date and time
echo ex: 20210713 14:30
read -p 'Date?  ' _date
read -p 'Time?  ' _time

sudo date -s "${_date} ${_time}"
