README.es.md

Este proyecto ha sido preparado para aprender las API chatgpt, iptv-org y tmdb. Los códigos fueron escritos enteramente por chatgpt, así que no sé qué falta, qué es demasiado o qué está mal. No sé si puedo hacer algún arreglo con respecto a cualquiera de sus solicitudes en el futuro. En el archivo final m3utostrm.py, todas las explicaciones, instrucciones y configuraciones están en inglés. Sin embargo, en las versiones antiguas, en la carpeta 'old_versions', dice turco, que es mi propio idioma. Lo siento si esto será un problema para aquellos que quieran utilizar versiones anteriores.

Utiliza Python para escanear el contenido de los archivos '.m3u' descargados de proveedores de servicios de IPTV y crear archivos '.strm' para películas y programas de televisión. También crea archivos '.nfo' utilizando la API TMDB y organiza transmisiones de televisión en archivos '.m3u' con la API IPTVORG.

La aplicación sigue la siguiente ruta para realizar estas operaciones:
1) Instale las bibliotecas de Python que se utilizarán si no están instaladas,

2) Descarga el archivo '.m3u' con la información del proveedor de iptv proporcionada por el usuario, nombrándolo de acuerdo con la fecha y hora de ejecución de la aplicación,

3) Si no hay otros archivos '.m3u' en la carpeta donde se encuentra el archivo '.m3u' descargado, también lo guardará como un archivo 'tobeprocess.m3u'.

4) Si hay otros archivos '.m3u' en la carpeta donde se encuentra el archivo '.m3u' descargado, encuentra el más actual mirando sus nombres.

5) Guarda las líneas de URL que no están en el archivo '.m3u' más reciente que encuentra, pero que están en el archivo '.m3u' recién descargado, como archivo 'tobeprocess.m3u'.

6) Realiza un seguimiento del número restante de transacciones contando las URL en el archivo 'tobeprocess.m3u'.

7) Crea carpetas 'películas' para películas, carpetas 'series' para series de televisión y carpetas 'porn' para contenido porno para guardar archivos '.strm' y '.nfo'.

8) Edita los nombres de las transmisiones de canales iptv con el patrón de sufijo en el código,

9) Crea archivos '.strm' en la carpeta 'porn' para 'urls' cuyo nombre es adecuado para nombrar porno,

10) Usando la clave API de Tmdb, separa las 'URL' restantes en películas y series de televisión,

11) Crea una carpeta con su propio nombre para cada película dentro de la carpeta 'movies', y crea un archivo '.strm' en el que está escrita la 'url' de la película y un archivo '.nfo' que contiene información tomada del sitio tmdb,

12) Crea una carpeta con nombre propio para cada serie dentro de la carpeta 'series', esta carpeta también crea una carpeta para las temporadas y crea un archivo '.strm' en el que se escribe la 'url' de la serie y un ' Archivo .nfo' que contiene la información obtenida del sitio tmdb,

13) Crea un nuevo archivo llamado 'updated_channels.m3u' para transmisiones de canales iptv en el archivo '.m3u' descargado y edita su contenido con la API iptv-org,


Mejoras previstas a realizarse;
- Opción para descargar el archivo '.m3u' o procesar un archivo existente,
