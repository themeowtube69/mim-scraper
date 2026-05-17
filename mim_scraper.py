import requests, json, csv, time, os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY","")
OUTPUT_FILE = "mim_programs.csv"
UNIVERSITIES = [
        (2,"Imperial College London","UK","https://www.imperial.ac.uk/business-school/masters/management/"),
        (39,"London School of Economics","UK","https://www.lse.ac.uk/management/study/msc-management"),
        (45,"Warwick Business School","UK","https://warwick.ac.uk/study/postgraduate/courses/mscmanagement/"),
        (61,"HEC Paris","France","https://www.hec.edu/en/master-s-programs/grande-ecole-program-master-in-management"),
        (62,"ESCP Business School","France","https://escp.eu/programmes/master-in-management"),
        (64,"IE Business School","Spain","https://www.ie.edu/business-school/master-programs/master-in-management/"),
        (66,"Bocconi University","Italy","https://www.unibocconi.eu/wps/wcm/connect/bocconi/sitopubblico_en/navigation+tree/home/programs/master+of+science/management"),
        (92,"Duke Fuqua MiM","USA","https://www.fuqua.duke.edu/programs/masters/management-mim"),
]
def read_page(url):
            try:
                            r=requests.get("https://r.jina.ai/"+url,headers={"User-Agent":"Mozilla/5.0"},timeout=35)
                            return r.text
except Exception as e:
        print("Error:"+str(e),flush=True)
        return ""

def analyze(name,text):
            prompt="Researcher. May 2026. From "+name+" website extract MiM/MSc Management info for Autumn 2026. Text:"+text[:10000]+"\nReturn ONLY JSON:{\"program_name\":\"name or Not Available\",\"status\":\"OPEN or CLOSED or UNCLEAR\",\"deadline\":\"date or Not Specified\",\"tuition_fees\":\"fees or Not Specified\",\"scholarships\":\"names or Not Specified\"}"
            try:
                            r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+GROQ_API_KEY,"Content-Type":"application/json"},json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"temperature":0.1},timeout=30)
                            data=r.json()
                            if "error" in data: raise Exception(str(data["error"]))
                                            c=data["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip()
                            return json.loads(c)
except Exception as e:
        print("Groq:"+str(e),flush=True)
        return None

def main():
            print("=== MiM Scraper START ===",flush=True)
            with open(OUTPUT_FILE,"w",newline="",encoding="utf-8") as f:
                            csv.writer(f).writerow(["Rank","University","Country","Program","Status","Deadline","Fees","Scholarships","Link"])
                        saved=skipped=0
    for rank,name,country,url in UNIVERSITIES:
                    print("\n["+str(rank)+"] "+name,flush=True)
                    text=read_page(url)
                    if not text or len(text)<200:
                                        print("  SKIP",flush=True)
                                        skipped+=1
                                        continue
                                    print("  OK "+str(len(text))+"chars. Analyzing...",flush=True)
        result=analyze(name,text)
        if not result:
                            skipped+=1
                            time.sleep(4)
                            continue
                        st=result.get("status","UNCLEAR")
        print("  "+result.get("program_name","")+"|"+st+"|"+result.get("deadline",""),flush=True)
        if st!="CLOSED":
                            with open(OUTPUT_FILE,"a",newline="",encoding="utf-8") as f:
                                                    csv.writer(f).writerow([rank,name,country,result.get("program_name",""),st,result.get("deadline",""),result.get("tuition_fees",""),result.get("scholarships",""),url])
                                                print("  SAVED",flush=True)
            saved+=1
else:
            print("  CLOSED",flush=True)
        time.sleep(4)
    print("=== DONE Saved:"+str(saved)+" Skipped:"+str(skipped)+" ===",flush=True)
main()
