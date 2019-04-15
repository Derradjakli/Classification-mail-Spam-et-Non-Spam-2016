import email
import re
import numpy as np
import matplotlib.pyplot as plt

print("predit_email(spam[:100]+nospam[:100],[spam[:20],nospam[:20]])")

def read_file(fname):
    """ Lit un fichier compose d'une liste de emails, chacun separe par au moins 2 lignes vides."""
    f = open(fname,'rb')
    raw_file = f.read()
    f.close()
    raw_file = raw_file.replace(b'\r\n',b'\n')
    emails =raw_file.split(b"\n\n\nFrom")
    emails = [emails[0]]+ [b"From"+x for x in emails[1:] ]
    return emails

def get_body(em):
    """ Recupere le corps principal de l'email """
    body = em.get_payload()
    if type(body) == list:
        body = body[0].get_payload()
    try:
        res = str(body)
    except Exception:
        res=""
    return res

def clean_body(s):
    """ Enleve toutes les balises html et tous les caracteres qui ne sont pas des lettres """
    patbal = re.compile('<.*?>',flags = re.S)
    patspace = re.compile('\W+',flags = re.S)
    return re.sub(patspace,' ',re.sub(patbal,'',s))

def get_emails_from_file(f):
    mails = read_file(f)
    return [ s for s in [clean_body(get_body(email.message_from_bytes(x))) for x in mails] if s !=""]

spam = get_emails_from_file("spam.txt" )
nospam = get_emails_from_file("nospam.txt")

def split(liste,x):
    n=len(liste)
    return (liste[:(int)(x*n/100)+1],liste[(int)(x*n/100)+1:])

def long_mail(texte):
    cpt=0
    texte+=" "
    if len(texte)==0:
        return cpt
    j='a'
    for i in texte:
        if i==" ":
            if j!=i: # on évite de compter deux espaces successifs comme un mot 
                cpt+=1
        j=i
    return cpt

def histg(liste_nom):
    L=[long_mail(i) for i in liste_nom]
    plt.hist(L,range(max(L)+1))
    plt.title("histogramme des non-spams: nombre de mails pour x mots")
    plt.show()
    return 0

def apprend_modele(spam,nonspam):
    p=len(spam)/(1.0*len(nonspam+spam))
    Lspam=[long_mail(i) for i in spam]
    Lnonspam=[long_mail(i) for i in nonspam]
    Hspam=np.histogram(Lspam,max(Lspam+Lnonspam)+1)[0]
    Hnonspam=np.histogram(Lnonspam,max(Lspam+Lnonspam)+1)[0]
    Hspam=Hspam*(p/(1.0*len(spam+nonspam)))
    Hnonspam=Hnonspam*((1-p)/(1.0*len(spam+nonspam)))
    return [Hspam,Hnonspam] #Hspam, Hnonspam la distribution de P(X=x | Y=1), P(X=x | Y=-1)

def plus_proche(L,n):
    for i in range(len(L)):
        if(n+i<len(L)):
            if L[n+i]>0:
                return i
        if(n-i>=0):
            if L[n-i]>0:
                return i
    return 0

def predit_email(emails,modele):
    M=apprend_modele(modele[0],modele[1])
    L=[]
    P_y=len(modele[0])/(1.0*(len(modele[0])+len(modele[1])))
    Spam=[]
    Nonspam=[]
    for email in emails:
        n=long_mail(email)
        if(n>=len(M[0])):
            n=len(M[0])-1
        if(M[0][n]==0 and M[1][n]==0):
            M[0][n]=plus_proche(M[0],n)
            M[1][n]=plus_proche(M[1],n)
            
        if M[0][n]*P_y>M[1][n]*(1-P_y):
            Spam.append(email)
        else:
            Nonspam.append(email)
    return Nonspam[1]


