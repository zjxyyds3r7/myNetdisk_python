import uvicorn
from fastapi import FastAPI, Request
from fastapi import File
from fastapi import UploadFile
import pickle as pk
import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
import os
import shutil
app = FastAPI()
templates = Jinja2Templates(directory="html")

file_info = []
key = 'key'
with open('file.pk', 'rb') as f:
    file_info = pk.load(f)


def save_pk():
    with open('file.pk', 'wb') as f:
        pk.dump(file_info, f)


def get_html(file_name):
    html_file = open(f"html/{file_name}", 'r').read()
    return html_file


@app.get("/", response_class=HTMLResponse)
async def root():
    return get_html('index.html')


@app.get("/index", response_class=HTMLResponse)
async def root():
    return get_html('index.html')


@app.post('/uploadfile', response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    global file_info
    if len(file_info) > 100:
        return "<h1>提交失败 没地方了</h1>"
    if file.size > 5 * 10**7:
        return f"<h1>提交失败 文件太大了 文件足足有{file.size}字节</h1>"

    if file.size == 0 or file.filename == "":
        return f"<h1>提交失败 文件大小异常</h1>"
    file_content = await file.read()
    file_name = '.'.join(file.filename.split('.')[0:-1]) + \
                f'.{datetime.datetime.now().strftime("%Y %m %d %H %M %S")}.' + \
                file.filename.split('.')[-1]
    print(file_name)
    with open(f'file/{file_name}', 'wb') as f:
        f.write(file_content)
    _f = {'name': file_name, 'time': f'{datetime.datetime.now()}'}
    file_info.append(_f)
    save_pk()
    return "<h1>提交成功</h1>"


@app.get("/download")
async def download(request: Request):
    return templates.TemplateResponse(
        'download.html', {'request': request, 'link_list': file_info}
    )


@app.get("/api/download/{file_name}", response_class=HTMLResponse)
async def get_file(file_name):
    if file_name not in [i['name'] for i in file_info]:
        return "<h1>File not found</h1>"
    out = '.'.join(file_name.split('.')[:-2])+'.'+file_name.split('.')[-1]
    return FileResponse(
        'file/'+file_name, filename=out,
    )


@app.get(f"/api/del/{key}/all", response_class=HTMLResponse)
async def clear():
    global file_info
    file_info = []
    save_pk()

    shutil.rmtree('file')
    os.mkdir('file')
    return "<h1>清理完毕</h1>"


@app.get("/api/del/"+ key + "/{number}", response_class=HTMLResponse)
async def clear_num(number: int):
    global file_info
    del_list = file_info[:number]
    file_info = file_info[number:]
    save_pk()
    for d in del_list:
        try:
            os.remove('file/'+d['name'])
        except:
            pass
    return f"<h1>清理了{len(del_list)}个文件</h1>"


if __name__ == '__main__':
    uvicorn.run(app='main:app', host="0.0.0.0", port=1101)