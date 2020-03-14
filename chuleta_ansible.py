### Cheat sheet Ansible ###

## Inventario: lista de servidores con los cuales interactuar

# Abrir el archivo del Inventario
sudo vi /etc/ansible/hosts

# Ejemplo de inventario
blue.example.com
192.168.0.1

# La primera linea es equivalente a las proximas 3
db[1:3].makigas.es  =   db1.makigas.es
                        db2.makigas.es
                        db3.makigas.es

# Agrupar servidores por grupos
[webservers]
alpha.example.org
192.168.1.100

[dbservers]
db01.intranet.mydomain.net
db02.intranet.mydomain.net
10.25.1.56
10.25.1.57

## Comandos Ad-Hoc
# Uso de ansible con el modulo Ping a servidor especifico del inventario
ansible makigas.es -m ping

# Uso de ansible con el modulo Ping a servidor especifico del inventario usando otro archivo de inventario
ansible danirod.es -m ping -i hosts.txt

# Uso de ansible con el modulo shell (por defecto si no se especifica) 
ansible makigas.es -a 'echo hola'
ansible makigas.es -m shell -a 'echo hola'
    # Salida $1=servidor donde fue ejecutado - $2=estado de la ejecucion - $3=codigo de salida del proceso - $4=salida estandar el proceso
    """ 
    makigas.es | SUCCESS | rc=0 >>
    hola
    """
# Uso de ansible con el modulo shell usando el comando true que siempre devuelve cero (0)
ansible makigas.es -a 'true'
    # Salida
    """
    makigas.es | SUCCESS | rc=0 >>
    
    """
# Uso de ansible con el modulo shell usando el comando false que siempre devuelve uno (1)
ansible makigas.es -a 'false'
    # Salida
    """
    makigas.es | FAILED | rc=1 >>
    
    """

# Uso de ansible con el modulo shell usando el comando 'ls /' que devuelve el contenido de la raiz del servidor remoto
ansible makigas.es -a 'ls /'

# Uso de ansible con el modulo shell usando el comando 'uname' que devuelve informacion del sistema operativo, su version, kernel, etc.
ansible makigas.es -a 'uname'

# Uso de ansible con el modulo apt pasando parametros del nombre del paquete (vim) y el estado en que se tiene que encontrar (present) que significa que tiene que estar instalado
ansible makigas.es -m apt -a 'name=vim state=present'

# Uso de ansible con el modulo apt pasando parametros del nombre del paquete (vim) y el estado en que se tiene que encontrar (present) que significa que tiene que estar instalado
# -b: con modo become para correr las instrucciones con usuario root
# -K: para que pregunte por contraseña
ansible makigas.es -m apt -a 'name=vim state=present' -b -K




## PlayBooks: archivos en lenguaje yaml que se organizan como objetos en los cuales se pueden especificar claves con sus respectivos valores de configuracion

# Crear un playbook
vi ejemplo.yml
    # Ejemplo de un playbook: a todos los servidores en el inventario se instalara vim con modulo apt como superusuario
    # ademas se imprimira un saludo sin superusuario 
    # ademas se detendra el servicio nginx sin superusuario
    """
    ---

    - hosts: all
      tasks:
      - name: instala vim
        apt: name=vim state=present
        become: true
      - name: saluda
        shell: echo hola
      - name: detiene nginx
        service: name=nginx state=stopped
    """
# Ejecutar un playbook y que pida la contraseña
ansible-playbook tareas.yml -K

 



## Archivos de configuracion  

# Editar archivo de configuracion, el nombre por defecto que toma es ansible.cfg, si se quiere renombrar el archivo se debe especificar que archivo tiene que tomar ansible
/etc/ansible/ansible.cfg

# Para especificar el nombre de un archivo de configuracion se puede hacer de la siguiente forma
ANSIBLE_CONFIG=foo.cfg ansible -i hosts.txt webservers -m ping

# Ejemplo de archivo de configuracion, donde se indica el usuario remoto con el cual conectarse
"""
[defaults]
remote_user = vagrant
"""

# Parametros usuales
inventory = /etc/ansible/hosts # señala la ubicación del inventario que utiliza Ansible para conocer los hosts disponibles
roles_path = /etc/ansible/roles # indica la ubicación donde el Ansible Playbook tiene que buscar roles adicionales
log_path = /var/log/ansible.log # señala la ubicación donde se almacena los logs de Ansible. El permiso para escribir en este archivo debe darse al usuario de Ansible.
retry_files_enabled = False # indica la función de reintento que permite a Ansible crear un archivo .retry cada vez que falla un Playbook. Se recomienda dejar esta opción deshabilitada a menos que realmente lo desees, ya que si está habilitada, creará varios archivos que ocuparán bastante espacio
host_key_checking = False # este parámetro se utiliza en entornos que cambian constantemente, donde se eliminan los hosts antiguos y host nuevos toman su lugar. Este parámetro se usa generalmente en una nube o en un entorno virtualizado.
forks = 5 # Indica la cantidad de tareas paralelas que se pueden ejecutar en el host del cliente. De forma predeterminada, el valor de esta propiedad es 5 y esto permite ahorrar recursos del sistema y ancho de banda de la red, pero en caso de que tengas suficientes recursos y un buen ancho de banda, puede aumentar el número.
remote_port = 22 # contiene el número de puerto utilizado por SSH en los hosts
nocolor = 0 # Le da la posibilidad de usar diferentes colores para el libro de jugadas y las tareas de Ansible que muestran errores y éxitos

# Ejemplo con ansible-playbook especificando usuario 'vagrant' para conectarse
vim playbook.yml
"""
---

- hosts: all
  remote_user: vagrant
  tasks:
  - name: "Lanza un ping"
    ping:
"""
ansible-playbook -i hosts.txt playbook.yml

## Handlers: son mecanismos que permiten pedirle a ansible que cuando logre correr una tarea satisfactoriamente (SUCCESS) notifique para que pasen otras cosas
# tambien son tareas, tienen la misma sintaxis, tienen parametros y modulos
# no se corren de forma lineal de arriba a abajo

# Ejemplo: 
# un playbook que ejecute en todos los hosts, con usuario vagrant, convirtiendose a superusuario, la tarea 'Instala Apache2', usando el modulo apt, pasando siguientes parametros:
# nombre del software a instalar sera apache2
# el estado es presente, es decir, tiene que estar instalado
# y tambien que actualize la cache para que no surjan problemas en la instalacion
# ademas se activara el handler "Reinicia el servidor web" de ejecutarse exitosamente la tarea
# Se declararan un handler de nombre 'Reinicia el servidor web'
# usando el modulo service (para manejo de servicios en linux) que manejara el servicio apache2
# y el estado de este sera restarted, para que ansible reinicie el servicio
vim playbook.yml
"""
---

- hosts: all
  remote_user: vagrant
  become: true
  tasks:
  - name: Instala Apache2
    apt: name=apache2 state=present update_cache=true
    notify:
      - "Reinicia el servidor web"
  handlers:
  - name: Reinicia el servidor web
    service: name=apache2 state=restarted
"""
ansible-playbook -i hosts.txt playbook.yml -K 