import os
import json
import sys
import shutil
import cherrypy
import tempfile
import pdb#DEBUG

#TODOs...
# TODO: Fix the java support (so it actually works)
# TODO: Fix the shell scripts (so they work with arguments)
# TODO: Make the java pages support arguments

class Request(object):
	def __init__(self, **options):
		for name in options:
			setattr(self,name,options[name])
		
	
	path=""
	filepath=""
	contents=""
	args={}
	config={}

def safeeval(fdsfjalsjkdhfasdk, request):#To prevent the servlet from using the same variable names(only for the first)
	exec(fdsfjalsjkdhfasdk)


def parse(path,filepath,con,args,config):
	pagecon=con
	try:
		f=open(os.path.join(os.path.dirname(filepath),"WEB-INF","info.json"))
		servlets=json.decode(f.read())
		name=path[-1]
		arr=name.split(".")
		ext=arr[-1]
		for servlet in servlets:
			if servlet["ext"]==ext or servlet["all"]:
				svt=open(os.path.join(os.path.dirname(filepath),"WEB-INF",servlet["file"]))
				code=svt.read()
				svt.close()
				f.close()
				oldout=sys.stdout
				tmp=tempfile.mkstemp(dir=config["tmp"])
				sys.stdout=open(tmp[1],'w')
				safeeval(code,Request(path=path,filepath=filepath,contents=con,args=args,config=config))
				sys.stdout.close()
				sys.stdout=oldout
				f=open(tmp[1])
				stuff=f.read()
				f.close()
				os.remove(tmp[1])
				return stuff
			
		
		f.close()
	except IOError: pass
	if con.find("#python script")==0:
		oldout=sys.stdout
		tmp=tempfile.mkstemp(dir=config["tmp"])
		sys.stdout=open(tmp[1],'w')
		safeeval(con,Request(path=path,filepath=filepath,con=con,args=args,config=config))#os.popen("%s '%s'"%(config["python"],filepath)).read()
		sys.stdout.close()
		sys.stdout=oldout
		f=open(tmp[1])
		stuff=f.read()
		f.close()
		os.remove(tmp[1])
		return stuff
	elif con.find("//java script")==0:
		jcachedir=os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),config["java"]["cachedir"])
		at2=path
		at2[-1]=at2[-1].replace(".java",".class")
		try:
			open(os.path.join(jcachedir,",".join(at2))).close()
		except IOError:
			comp=os.popen("%s '%s' -d '%s'"%(config["java"]["javac"],filepath,jcachedir))
			err=comp.read()
			if comp.close():
				raise cherrypy.HTTPError(500,err)
			
		
		#os.rename(os.path.join(jcachedir,path[-1]),os.path.join(jcachedir,",".join(path)))
		arr=path
		arr[-1]=arr[-1].replace(".java","")
		print os.path.join(jcachedir,path[-1].replace(".java","").replace(".class",""))#DEBUG
		os.rename(os.path.join(jcachedir,path[-1].replace(".java","").replace(".class","")),os.path.join(jcachedir,",".join(at2))+".class")
		pagecon=os.popen("%s '%s'"%(config["java"]["java"],os.path.join(jcachedir,",".join(arr))))
		if not config["java"]["cacheon"]:
			os.remove(os.path.join(jcachedir,",".join(path)))
		
	elif con.find("#shell script")==0:
		f=open(filepath)
		code=f.read()
		prefix=""
		f.close()
		fp=tempfile.mkstemp(dir=config["tmp"])[1]
		tmps=[fp]
		fp_tmp=""
		f_tmp=None
		for arg in args:
			fp_tmp=tempfile.mkstemp(dir=config["tmp"])[1]
			f_tmp=open(fp_tmp,'w')
			f_tmp.write(args[arg])
			f_tmp.close()
			tmps.append(fp_tmp)
			prefix=prefix+"$%s=`cat '%s'`\n"%(arg,fp_tmp)
		
		f=open(fp,'w')
		f.write("%s\n%s"%(prefix,code))
		f.close()
		cde=os.popen("%s '%s'"%(config["sh"],fp)).read()
		for tmp in tmps: os.remove(tmp)
		return cde
	
	return pagecon
