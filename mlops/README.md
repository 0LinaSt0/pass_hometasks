# AIRFLOW SETUP

## ~~~> 1. Virtualenv:
```bash
python3.8 -m venv .venv;
source .venv/bin/activate;
pip install --upgrade pip;
```

## ~~~> 2. Install and setup MySQL
```bash
sudo apt-get install mysql-server && sudo /etc/init.d/mysql start.;

sudo mysql_secure_installation;
sudo mysql -u root -p;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '<PASSWD>';

sudo nano /etc/mysql/my.cnf;
    # [mysqld]
    # port = 33061

sudo apt-get install build-essential \
    && sudo apt-get install python3.8-dev libmysqlclient-dev \
    && sudo apt install pkg-config;

sudo service mysql restart;

pip install mysqlclient;
```

And don't forget to create airflow user:
```sql
CREATE DATABASE Airflow;
CREATE USER 'Airflow'@'%' IDENTIFIED WITH mysql_native_password BY -- <YOU PSWD>;
GRANT USAGE, EXECUTE ON *.* TO 'Airflow'@'%';
GRANT ALL PRIVILEGES ON Airflow.* TO 'Airflow'@'%';

SELECT user, host FROM mysql.user WHERE user='Airflow';
SHOW GRANTS FOR 'Airflow'@'localhost';
```

## ~~~~~~~> 3. Install and setup Airflow
```bash
pip install apache-airflow==2.7.3 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.8.txt" --force-reinstall --upgradepip uninstall tenacity;

cp sources/airflow.cfg /home/airflow/airflow.cfg;

sudo mkdir /home/airflow && sudo mkdir /home/airflow/dags &&  sudo chmod -R 777 /home;
export AIRFLOW_HOME=/home/airflow;
airflow db migrate;

airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin;
```

## ~~~~~~~> 4. Start Airflow
```bash
sudo service mysql restart &&\
    export AIRFLOW_HOME=/home/airflow && \
    (airflow scheduler & airflow webserver -p 8080);

    # Look at http://localhost:8080 
```