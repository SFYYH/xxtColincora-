@echo off

chdir | cd

python --version >nul 2>nul
if %ERRORLEVEL% == 0 (
    goto start
) else (
    echo ϵͳ��δ�ҵ� Python
    echo ��ȷ��ϵͳ���Ƿ��а�װ Python
    echo ���а�װ Python �����û������ Python ��������
    echo ��û�а�װ Python �ɷ��������ַ���� Python3.9.0 ��װ��
    echo https://cdn.npmmirror.com/binaries/python/3.9.0/python-3.9.0.exe
    echo ע�� Python ��Ҫ��װ3.9.0�����ϰ汾
    pause
    exit 0
)

:start
if exist ".\venv" (
    .\venv\Scripts\python.exe .\faithlearning.py
) else (
    echo ��ǰĿ¼δ�ҵ����⻷��
    echo ����Ϊ�㴴�����⻷��
    python -m venv .\venv
    echo ���⻷�������ɹ�
    goto start
)
pause
exit 0