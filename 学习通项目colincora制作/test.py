import requests
url="https://mooc1-2.chaoxing.com/mycourse/studentstudy?chapterId=629567677&courseId=227527666&clazzid=60997649&enc=2cd270d84aaaf7bd0dcb1efc5b40adae"
headers={
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Length': '98',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'route=3744838b34ea6b4834cd438e19ed44f0; JSESSIONID=9CD969F9C1B9633A46EAD7880736DD51; fanyamoocs=11401F839C536D9E; fid=314; isfyportal=1; ptrmooc=t',
    'Host': 'passport2.chaoxing.com',
    'Origin': 'https://passport2.chaoxing.com',
    'Referer': 'https://passport2.chaoxing.com/login?loginType=4&fid=314&newversion=true&refer=http://i.mooc.chaoxing.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': "k8s=1676210582.924.43832.400747; route=440ceb57420433374ff0504da9778fc7; lv=4; fid=2867; _uid=197121073; UID=197121073; vc=EF3F9F09333D58CC27F42EB493F1C9E2; vc2=0EECB57284169C764A242F3F48472B0A; xxtenc=7f800688465d708d2ba2a2bd295e6025; _dd83523724=1676215559773; fanyamoocs=ACBD3600079851A18351C072BAF36DBE; uf=da0883eb5260151ea8eb41a322fba4108f7d06d2cf363bd51fc456b97ec44b2e23a83ea7fbdc54cc3284d6281e40d9cc913b662843f1f4ad6d92e371d7fdf6441e50d77142964ec0ce915f659a7402a8db9a01fd759e1b98e785ea7d473590487c3fa94f30d997c3; _d=1676215580270; vc3=fHPRe4ubZ8pevQSYj3XuIIhoP%2Fr7CIz7Zn6gH2U0iuf7KuTsLERqY%2FltT%2F0TFLe1%2BXae7nPpWAplyKzDtXYGPE36xyrfLoj0LbTl9N7DKMZxXAKSkhghNXUFcpQ1gW02iC0%2Fu1s8voh3uCiQ1FNL8ojjEJdHUAysK5E4VDIZYbo%3D3cff13d0abf9b1313f9170966ed5815d; DSSTASH_LOG=C_38-UN_1715-US_197121073-T_1676215580272; source=""; thirdRegist=0; _dd197121073=1676215660329; jrose=E269A8C4AE567F6BB726F11CA1921A01.mooc-2592781376-1d6nt"
}
data={
    "chapterId": "629567677",
    "courseId": "227527666",
    "clazzid": "60997649",
    "enc": "2cd270d84aaaf7bd0dcb1efc5b40adae"
}
resp=requests.get(url,headers=headers,data=data)
print(resp.text)