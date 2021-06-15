import os

from utils.postgis import postgis_connection
from utils.geoserver import geoserver_connection
from utils.init_manager import init_manager

postgres_user       = os.environ.get('POSTGRES_USER', 'admin')
postgres_password   = os.environ.get('POSTGRES_PASS', 'password')
postgres_port       = os.environ.get('POSTGRES_PORT', '5432')
postgres_host       = os.environ.get('POSTGRES_HOST', 'db')
postgres_dbname     = os.environ.get('POSTGRES_DBNAME', 'sigweb')

geoserver_user      = os.environ.get('GEOSERVER_ADMIN_USER', 'admin')
geoserver_password  = os.environ.get('GEOSERVER_ADMIN_PASSWORD', 'password')
geoserver_port      = os.environ.get('GEOSERVER_PORT', '8080')
geoserver_host      = os.environ.get('GEOSERVER_HOST', 'geoserver')
geoserver_workspace = os.environ.get('GEOSERVER_WORKSPACE', 'sigweb_workspace')

scripts_dir         = os.environ.get('SQL_SCRIPTS', 'sql_scripts')

pg_conn = postgis_connection(host     = postgres_host,
                             port     = postgres_port,
                             database = postgres_dbname,
                             user     = postgres_user,
                             password = postgres_password)

gs_conn = geoserver_connection(host     = geoserver_host,
                               port     = geoserver_port,
                               username = geoserver_user,
                               password = geoserver_password)

manager = init_manager(geo_conn       = gs_conn,
                       pgs_conn       = pg_conn,
                       workspace_name = geoserver_workspace,
                       scripts_dir    = 'sql_scripts')

manager.initialize()
manager.register_tables_from_scripts_dir()
