import email
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import random as rd

print("classifieur(spam[20:120]+nospam[20:120],[spam[:20],nospam[:20]])")
print("classifieur()")

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

def tst(v1,v2):
    return v1[0]*v2[0]

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

heur_accent_e=['é','è','ê','ê','ë']
heur_accent_a=['à']
heur_accent_u=['ù']
heur_accent_o=['ô']

def constr_mot(mail): #on construit la liste L des mots dans mail
    L=[]
    tmp=""
    for a in mail:
        if a!=' ':
            tmp+=a
        else:
            L.append(tmp)
            tmp=""
    return L

def heur_lettre(l):  #"normalise" la lettre par rapport aux heuristiques d'accent, de majuscule, de ponctuation vers une lettre de l'alphabet sans accent, en minuscule(lettre vide si non dans l'alphabet)
    if l in heur_accent_e:
        return 'e'
    if l in heur_accent_a:
        return 'a'
    if l in heur_accent_u:
        return 'u'
    if l in heur_accent_o:
        return 'o'
    if ord(l)-ord('A') in range(26):
        return chr(ord(l)-ord('A')+ord('a'))
    if ord(l)-ord('a') not in range(26):
        return ''
    return l


def heur_mot(mot): #construction du mot normalisé par rapport aux heuristiques
    m=""
    for l in mot:
        m+=heur_lettre(l)
    return m

def liste_mot(mail): #decompose le mail (chaine de caractère) en liste de mots normalisés par rapport aux heuristiques
        mail+=" "
        L=[]
        a=""
        for c in mail:
            if c!=' ':
                a+=c
            else:
                a=heur_mot(a)
                if a!="":
                    L.append(a)
                a=""
        return L

def choix_dico(emails,p): # p est le pourcentage (entre 0 et 1) de mot conservé dans le dico par rapport à ceux dans les emails, de celui apparaissant le plus vers celui apparaissant le moins
    L=[ [m for m in liste_mot(e)] for e in emails]
    N=[]
    M=[]
    d=dict()
    for i in L:
        for m in i:
            if m not in M:
                cpt=0
                for j in L:
                    if m in j:
                        cpt+=1
                M.append(m)
                N.append(cpt)
    #plt.hist(N,range(max(N)+2))
    #plt.xlabel("nombre d'iterations", fontsize=16)  
    #plt.ylabel("nombre de mots", fontsize=16)
    #plt.show()
    Ind=np.argsort([-i for i in N])
    Ind=Ind[:max((int)(p*len(Ind)),1)]
    for i in Ind:
        d.update({M[i]:N[i]})
    return d

def constr_mail(mail,dico): # construit X pour mail, à partir des mots de dico, renvoie un dictionnaire
    L=liste_mot(mail)
    d=dict()
    for m in dico.keys():
        if m in L:
            d.update({m:1})
        else:
            d.update({m:0})
    return d
        

def classifieur(emails,modele):         #modele de la forme: [spam,nonspam]
    Nspam=len(modele[0])
    Nnospam=len(modele[1])
    P_Y_1=(Nspam/(1.0*(Nspam+Nnospam))) #proba d'avoir Y=1: proportion de spam dans le modele
    
    dico_spam=choix_dico(modele[0],1-P_Y_1)
    dico_non_spam=choix_dico(modele[1],P_Y_1)
    
    dico=dict()                         #dictionnaire construit sur l'union des spams et non spams
    for m in dico_spam:
        dico.update({m:dico_spam[m]})
    for m in dico_non_spam:
        if m in dico.keys():
            dico[m]+=dico_non_spam[m]
        else:
            dico.update({m:dico_non_spam[m]})  
    Spam=[]     #liste des mails dans emails predits comme spam
    Non_spam=[] #liste des mails dans emails predits comme non spam
    for x in emails:
        mail=constr_mail(x,dico)
        tmp=0
        tmp2=0
        cptSpam=1
        cptNonspam=1
        for mot in mail.keys():
            if mot not in dico_spam.keys():
                if mail[mot]==1:
                    cptNonspam+=1
            else:
                tmp+=math.log((mail[mot]*(-Nspam+2*dico_spam[mot])+Nspam-dico_spam[mot])/(1.0*Nspam))
            if mot not in dico_non_spam.keys():
                if mail[mot]==1:
                    cptSpam+=1
            else:
                tmp2+=math.log((mail[mot]*(-Nnospam+2*dico_non_spam[mot])+Nnospam-dico_non_spam[mot])/(1.0*Nnospam))
                
        if abs((cptSpam-cptNonspam)/(1.0*(cptSpam+cptNonspam)))<0.1: #on etudie ici la fréquence d'apparition de mots apparaissant dans le mail et le dico spam mais pas dans le dico non-spam, et celle e mots apparaissant dans le mail et le dico non-spam mais pas dans le dico spam
            if tmp+math.log(P_Y_1)-tmp2+math.log(1-P_Y_1)>0:
                Spam.append(x)
            else:
                Non_spam.append(x)
        else:
            if cptSpam>cptNonspam:
                Spam.append(x)
            else:
                Non_spam.append(x)

    return Non_spam[52]

            
            
