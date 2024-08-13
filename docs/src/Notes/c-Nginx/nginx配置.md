
环境：Docker拉的Nginx镜像

## SSL证书下载

- 使用的是阿里云的免费证书，审核通过后将证书下载到本地，传到服务器上，注意下载的时候选择Nginx格式的
- 下载之后会得到一个SSL证书压缩包，解压后会得到`.key`和`.pem`文件

## Nginx配置SSL

- 修改配置文件`nginx.conf`

   ```shell
   worker_processes auto;
   
   events {
       worker_connections 1024;
   }
   http {
       log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                         '$status $body_bytes_sent "$http_referer" '
                         '"$http_user_agent" "$http_x_forwarded_for"';
   
       access_log /var/log/nginx/access.log main;
       error_log /var/log/nginx/error.log;
   
   		# 访问80端口时强制跳转443
       server {
           listen 80; 
           server_name xyfv.cn; # 配域名
           rewrite ^(.*)$ https://${server_name}$1 permanent;
       }
       server {
           listen 443 ssl; # 开启ssl,注意不同版本的写法
           # ssl on
           server_name xyfv.cn;
           ssl_certificate      /etc/nginx/ssl/xyfv.cn.pem; # pem文件
           ssl_certificate_key  /etc/nginx/ssl/xyfv.cn.key; # key文件
           ssl_session_timeout 5m;
           # 表示使用的加密套件的类型
           ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
           # 表示使用的TLS协议的类型
           ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
           ssl_prefer_server_ciphers on;
   
           location / {
               proxy_pass http://172.17.0.1:4000;  # 将请求转发到本地（宿主机）的 4000 端口
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }
       }
   }
          
   ```

- 注意：如果使用Nginx 1.15.0及以上版本，请使用`listen 443 ssl`代替`listen 443`和`ssl on`，否则可能报错：

  ```shell
  nginx: [emerg] unknown directive "ssl" in /usr/local/nginx/conf/nginx.conf
  ```

## 附

Docker-compose.yaml

```yaml
version: '3'

services:
  nginx:
    image: nginx:latest
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl  # 挂载 SSL 证书文件目录
      - ./logs:/var/log/nginx  # 挂载日志目录
      - ./html:/usr/share/nginx/html  # 挂载静态资源目录
    restart: always

```

