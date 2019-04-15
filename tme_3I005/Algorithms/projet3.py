import email
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import random as rd

print("classifieur(spam[0:100]+nospam[:100],[spam[:20],nospam[:20]])")

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

def distance_vect(v1,v2): #distance utilisée: similiraté cosinus
    if len(v2)!=len(v1):
        print("erreur de taille de vecteurs dans distance_vect")
        return 0
    cpt=0
    d1=0
    d2=0
    for i in range(len(v1)):
        cpt+=(v1[i]*v2[i])
        d1+=v1[i]**2
        d2+=v2[i]**2
    return cpt/(1.0*d1*d2)


def constr_liste_dist(x):
    n=len(x)
    L=[]
    for i in range(n):
        J=[]
        for j in range(n):
            J.append(math.exp(-distance_vect(x[i],x[j])))
        L.append(J)
    return L
    

def calcul_proba(x):
    n=len(x)
    L=constr_liste_dist(x)
    Res=[]
    for i in range(n):
        J=[]
        s=sum(L[i])-L[i][i]
        for j in range(n):
            J.append(L[i][j]/(1.0*s))
        Res.append(J)
    return Res

def main(emails):
    n=len(emails)
    P=calcul_proba(emails)
    Y=[]
    for i in range(n):
        Y.append([np.random.normal(0,0.5),np.random.normal(0,0.5)])
    ind=rd.randint(0,n-1)
    eps=10**(-2)
    Y[ind]=[Y[ind][k]-eps*a for k in [0,1]]
    




































            
            
