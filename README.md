# Django Demo

### 项目描述

- 实现后台定时异步发送邮件


### 第一步：安装Django并创建项目

使用pip命令安装Django.

```bash
pip install django==3.0.4 # 安装Django，所用版本为3.0.4
```

使用django-admin startproject

```bash
django-admin startproject myproject
```
### 第二步：安装redis和项目依赖的第三方包

项目中我们需要使用redis做Celery的中间人(Broker), 所以需要先安装redis数据库。redis网上教程很多，这里就简要带过了。

- **Windows下载地址：**https://github.com/MSOpenTech/redis/releases
- **Linux下安装（Ubuntu系统)**：$ sudo apt-get install redis-server

本项目还需要安装如下依赖包，你可以使用pip命令逐一安装。

``` bash
pip install redis==3.4.1 
pip install celery==4.4.2 
pip install eventlet # celery 4.0+版本以后不支持在windows运行，还需额外安装eventlet库
```

你还可以myproject目录下新建`requirements.txt`加入所依赖的python包及版本，然后使用`pip install -r requirements.txt`命令安装所有依赖。本教程所使用的django, redis和celery均为最新版本。

```
django==3.0.5
redis==3.4.1 
django_celery==3.3.1
celery==4.4.2  
eventlet # for windows only
```

### 第三步：Celery基本配置

1. 修改`settings.py`新增celery有关的配置。celery默认也是有自己的配置文件的，名为`celeryconfig.py`, 但由于管理多个配置文件很麻烦，我们把celery的配置参数也写在django的配置文件里。

```
# 配置celery时区，默认时UTC。
if USE_TZ:
    timezone = TIME_ZONE

# celery配置redis作为broker。redis有16个数据库，编号0~15，这里使用第1个。
broker_url = 'redis://127.0.0.1:6379/0'

# 设置存储结果的后台
result_backend = 'redis://127.0.0.1:6379/0'

# 可接受的内容格式
accept_content = ["json"]
# 任务序列化数据格式
task_serializer = "json"
# 结果序列化数据格式
result_serializer = "json"

# 可选参数：给某个任务限流
# task_annotations = {'tasks.my_task': {'rate_limit': '10/s'}}

# 可选参数：给任务设置超时时间。超时立即中止worker
# task_time_limit = 10 * 60

# 可选参数：给任务设置软超时时间，超时抛出Exception
# task_soft_time_limit = 10 * 60

# 可选参数：如果使用django_celery_beat进行定时任务
# beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

# 更多选项见
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
```

2. 在`settings.py`同级目录下新建`celery.py`，添加如下内容:

```
# coding:utf-8
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 指定Django默认配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# 为我们的项目myproject创建一个Celery实例。这里不指定broker容易出现错误。
app = Celery('myproject', broker='redis://127.0.0.1:6379/0')

# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')

# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks()

# 用于测试的异步任务
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


```

3. 打开`settings.py`同级目录下的`__init__.py`，添加如下内容, 确保项目启动时即加载Celery实例

```
# coding:utf-8
from __future__ import absolute_import, unicode_literals

# 引入celery实例对象
from .celery import app as celery_app
__all__ = ('celery_app',)
```

### 第四步：启动redis，测试celery是否配置成功

在Django中编写和执行自己的异步任务前，一定要先测试redis和celery是否安装好并配置成功。

首先你要启动redis服务。windows进入redis所在目录，使用`redis-server.exe`启动redis。Linux下使用`./redis-server redis.conf`启动，也可修改redis.conf将daemonize设置为yes, 确保守护进程开启。

启动redis服务后，你要先运行`python manage.py runserver`命令启动Django服务器（无需创建任何app)，然后再打开一个终端terminal窗口输入celery命令，启动worker。

```
# Linux下测试
Celery -A myproject worker -l info

# Windows下测试
Celery -A myproject worker -l info -P eventlet
```
如果你能看到[tasks]下所列异步任务清单如debug_task，以及最后一句celery@xxxx ready, 说明你的redis和celery都配置好了，可以开始正式工作了。
```bash

-------------- celery@DESKTOP-H3IHAKQ v4.4.2 (cliffs)
--- ***** -----
-- ******* ---- Windows-10-10.0.18362-SP0 2020-04-24 22:02:38

- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         myproject:0x456d1f0
- ** ---------- .> transport:   redis://127.0.0.1:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (eventlet)
  -- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
  --- ***** -----
   -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . myproject.celery.debug_task

[2020-04-24 22:02:38,484: INFO/MainProcess] Connected to redis://127.0.0.1:6379/0
[2020-04-24 22:02:38,500: INFO/MainProcess] mingle: searching for neighbors
[2020-04-24 22:02:39,544: INFO/MainProcess] mingle: all alone
[2020-04-24 22:02:39,572: INFO/MainProcess] pidbox: Connected to redis://127.0.0.1:6379/0.
[2020-04-24 22:02:39,578: WARNING/MainProcess] c:\users\missenka\pycharmprojects\django-static-html-generator\venv\lib\site-packages\celery\fixups\django.py:203: UserWarning: Using sett
ings.DEBUG leads to a memory
            leak, never use this setting in production environments!
  leak, never use this setting in production environments!''')
[2020-04-24 22:02:39,579: INFO/MainProcess] celery@DESKTOP-H3IHAKQ ready.
```


### 第五步：启动Django服务器和Celery服务

如果一切顺利，连续使用如下命令, 即可启动Django测试服务器。打开http://127.0.0.1:8000/即可看到我们项目开头的动画啦。注意：请确保redis和celery已同时开启。

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

如果没有创建管理账户
```
python manage.py createsuperuser
```

如果你要监控异步任务的运行状态（比如是否成功，是否有返回结果), 还可以安装flower这个Celery监控工具。

```
pip install flower
```

安装好后，你有如下两种方式启动服务器。启动服务器后，打开[http://localhost:5555](http://localhost:5555/)即可查看监控情况。

```bash
celery flower --broker=redis://127.0.0.1:6379/0
```



