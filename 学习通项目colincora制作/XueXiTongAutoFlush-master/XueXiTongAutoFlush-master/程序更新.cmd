@echo off
set filename="newData.zip"
echo �������س���

chdir | cd

C:\Windows\System32\WindowsPowerShell\v1.0\powershell curl -o %filename% "https://github.com/Levitans/XueXiTongAutoFlush/archive/refs/heads/master.zip"
if %ERRORLEVEL% == 0 (
    echo �������سɹ�
) else (
    echo ����������ӳ�ʱ
    echo ������
    pause
    exit 2
)

package\bin\unzip %filename%
xcopy /S/Y .\XueXiTongAutoFlush-master\package .\package
xcopy /Y .\XueXiTongAutoFlush-master\faithlearning.py .\

rmdir /S/Q XueXiTongAutoFlush-master
del /Q %filename%
echo ������³ɹ�
echo config.ini �ļ��ѱ����ǣ�ע�������������·������
pause