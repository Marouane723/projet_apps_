



from django.shortcuts import render, redirect



def home(request):
    return render(request, 'page/home.html')

from django.shortcuts import render, redirect

def probleme(request):
    if request.method == "POST":
        # Récupération des données du formulaire
        num_jobs = int(request.POST.get('num_jobs'))
        num_machines = int(request.POST.get('num_machines'))

        # Stockage des données dans la session
        request.session['num_jobs'] = num_jobs
        request.session['num_machines'] = num_machines

        # Redirection vers la page suivante
        return redirect('jobsdetail')  # Par exemple, vers un formulaire pour saisir les détails des jobs et machines

    return render(request, 'page/probleme.html')


from django.shortcuts import render, redirect


from django.shortcuts import render, redirect

def jobsdetail(request):
    # Récupérer le nombre de jobs et machines depuis la session
    num_jobs = request.session.get('num_jobs', 0)
    num_machines = request.session.get('num_machines', 0)

    # Définir les plages pour les jobs et machines
    job_range = range(1, num_jobs + 1)
    machine_range = range(1, num_machines + 1)

    if request.method == "POST":
        # Stocker les détails des jobs
        jobs = []

        for i in range(1, num_jobs + 1):
            job_data = {
                "job_id": i,
                "arrival_date": request.POST.get(f"arrival_date_{i}"),
                "delivery_date": request.POST.get(f"delivery_date_{i}"),
                "machine_times": [
                    {
                        "machine_id": j,
                        "preparation_time": int(request.POST.get(f"job_{i}_machine_{j}", 0))
                    }
                    for j in range(1, num_machines + 1)
                ],
            }
            jobs.append(job_data)

        # Stocker les données dans la session et rediriger
        request.session['jobs_details'] = jobs
        return redirect('contraint')

    return render(request, 'page/jobs.html', {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'job_range': job_range,
        'machine_range': machine_range,
    })


from django.shortcuts import render, redirect

def contraint(request):
    if request.method == "POST":
        # Récupérer la contrainte sélectionnée
        selected_contraint = request.POST.get('contraint')

        # Enregistrer dans la session
        request.session['contrainte'] = selected_contraint

        # Redirection vers une autre page (ou confirmation)
        if  request.session['contrainte'] == "SDST":
           return redirect('sdst')  # Exemple : redirection vers une autre vue
        elif  request.session['contrainte'] == "SIST":
            return  redirect('sist')
        else:

            return redirect('Demande')

    return render(request, 'page/contraint.html')



from django.shortcuts import render, redirect

def sdst(request):
    num_jobs = request.session.get('num_jobs', 0)
    num_machines = request.session.get('num_machines', 0)
    jobs_details = request.session.get('jobs_details', [])

    job_ids = [job["job_id"] for job in jobs_details]

    if request.method == "POST":
        setup_times = {}

        # Collecte des temps de réglage (SDST)
        for m in range(1, num_machines + 1):
            for i in job_ids:
                for j in job_ids:
                    field_name = f"setup_time_{i}_{j}_machine_{m}"
                    setup_time = int(request.POST.get(field_name, 0))
                    # Utiliser une clé en chaîne
                    setup_times[f"{i}_{j}_{m}"] = setup_time

        # Stockage dans la session
        request.session['setup_times'] = setup_times
        return redirect('Demande')  # Redirection après soumission

    return render(request, 'page/sdst.html', {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'job_ids': job_ids,
        'machine_range': range(1, num_machines + 1),
    })


from django.shortcuts import render, redirect

def Demande(request):
    if request.method == "POST":
        # Récupérer la méthode sélectionnée
        selected = request.POST.get('methode')  # Correspond au 'name' du champ HTML

        # Enregistrer dans la session
        request.session['methode'] = selected

        # Redirection basée sur le choix
        if selected == "optimisation":
            return redirect('optimisation')  # Redirection vers la vue 'optimisation'
        else:
            return redirect('regle')  # Redirection vers la vue 'regle'

    # Affichage de la page avec le formulaire
    return render(request, 'page/Demande.html')

def regle(request):
    if request.method == "POST":
        # Récupérer la règle de priorité sélectionnée
        selected_regle = request.POST.get('regle')

        # Enregistrer la règle dans la session
        request.session['regle'] = selected_regle

        # Redirection vers une autre page (par exemple : une page de confirmation ou vers une autre vue)
        if request.session.get('contrainte', 'Aucune contrainte')=="SDST":
          return redirect('sdst_gantt')  # Exemple : redirection vers une autre vue
        if request.session.get('contrainte', 'Aucune contrainte')=="SIST":
          return redirect('sist_gantt')
        if request.session.get('contrainte', 'Aucune contrainte')=="Aucun contrainte":
          return redirect('fifo_sanscontrainte')
        if request.session.get('contrainte', 'Aucune contrainte')==" No wait":
          return redirect('no_wait')




        else:
          return redirect('no_idle')

    return render(request, 'page/REGLE.html')

from django.shortcuts import render

def afficher_donnees(request):
    # Récupérer les données stockées dans la session
    num_jobs = request.session.get('num_jobs', 0)
    num_machines = request.session.get('num_machines', 0)
    jobs_details = request.session.get('jobs_details', [])
    contrainte = request.session.get('contrainte', 'Aucune contrainte')  # Correction ici
    regle = request.session.get('regle', 'Aucune règle')

    # Passer toutes ces informations au template
    return render(request, 'page/les_donnees.html', {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'jobs_details': jobs_details,
        'contrainte': contrainte,  # Correction ici
        'regle': regle,
    })

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render


def fifo_sanscontrainte(request):
    jobs_details = request.session.get('jobs_details', [])
    if request.session.get('regle', 'Aucune règle')=="FIFO":
      jobs_details.sort(key=lambda x: int(x["arrival_date"]))
    if request.session.get('regle', 'Aucune règle')=="LIFO":
      jobs_details.sort(key=lambda x: int(x["arrival_date"]), reverse=True)
    if request.session.get('regle', 'Aucune règle') == "SPT":

        jobs_details.sort(key=lambda x: sum(machine["preparation_time"] for machine in x["machine_times"]))


    if request.session.get('regle', 'Aucune règle') == "LPT":
        jobs_details.sort(key=lambda x: sum(machine["preparation_time"] for machine in x["machine_times"]),
                          reverse=True)
    if request.session.get('regle', 'Aucune règle') == "EDD":
        jobs_details.sort(key=lambda x: int(x["delivery_date"]))


    num_jobs = len(jobs_details)

    num_machines = request.session.get('num_machines', 0)


    s = [[0] * num_jobs for _ in range(num_machines)]
    c = [[0] * num_jobs for _ in range(num_machines)]
    n = num_jobs


    s[0][0] = int(jobs_details[0]["arrival_date"])
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])


    for i in range(1, num_jobs):
        preparation_time = int(jobs_details[i]["machine_times"][0]["preparation_time"])
        s[0][i] = max(int(jobs_details[i]["arrival_date"]), c[0][i - 1])
        c[0][i] = s[0][i] + preparation_time


    for i in range(1, num_machines):
        preparation_time = int(jobs_details[0]["machine_times"][i]["preparation_time"])
        s[i][0] = max(c[i - 1][0], int(jobs_details[0]["arrival_date"]))
        c[i][0] = s[i][0] + preparation_time
        for j in range(1, num_jobs):
            preparation_time = int(jobs_details[j]["machine_times"][i]["preparation_time"])
            s[i][j] = max(c[i - 1][j], c[i][j - 1])
            c[i][j] = s[i][j] + preparation_time
    # Calcul des retards
    tj = []  # Liste des retards
    for i in range(num_jobs):
        # Assurez-vous que delivery_date est convertible en entier
        delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du retard pour chaque job
        tj.append(max(0, finish_time - delivery_date))

    # Calcul du total et du retard maximum
    TT = sum(tj)  # Total des retards
    Tmax = max(tj) if tj else 0  # Retard maximum, vérifiez si la liste est vide

    # Calcul des Flow Times
    ftj = []  # Liste des flow times
    for i in range(num_jobs):
        # Assurez-vous que arrival_date est convertible en entier
        arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du flow time pour chaque job
        ftj.append(finish_time - arrival_date)

    # Calcul du total des Flow Times
    Tft = sum(ftj)
    combined_data = zip(ftj, tj)
    request.session['cmax'] = c[num_machines - 1][num_jobs - 1]
    fig, ax = plt.subplots(figsize=(10, 6))

    # Créer un dictionnaire de couleurs fixes pour chaque job_id
    job_colors = {job["job_id"]: f"C{idx}" for idx, job in
                  enumerate(sorted(jobs_details, key=lambda x: int(x["job_id"])))}

    for i in range(num_machines):
        for j in range(num_jobs):
            start = s[i][j]
            end = c[i][j]
            k = jobs_details[j]["job_id"]
            ax.barh(f"Machine {i + 1}",
                    end - start,
                    left=start,
                    color=job_colors[k],
                    edgecolor="black",
                    label=f"{k}" if i == 0 else "")

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt -Sans Contrainte")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Supprimer les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    # Trier les légendes par job_id
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: int(x[1]))
    handles, labels = zip(*sorted_pairs)
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=n)

    # Enregistrer le graphique dans un buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')

    # Combiner les données en une seule structure dans la vue
    combined_data = [
        {
            "job_id": job["job_id"],
            "arrival_date": job.get("arrival_date", 0),
            "delivery_date": job.get("delivery_date", 0),
            "flow_time": flow_time,
            "retard": retard,
        }
        for job, (flow_time, retard) in zip(jobs_details, zip(ftj, tj))
    ]

    return render(request, 'page/fifo_sanscontrainte.html', {
        'graph': graph,
        'regle': request.session.get('regle', 'Aucune règle'),
        'contrainte': request.session.get('contrainte', 'Aucune contrainte'),
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,  # Liste structurée des données
        'total_flow_time': Tft,
        'total_retard': TT,
        'max_retard': Tmax,
        'cmax': request.session['cmax']
    })


import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render



def sdst_gantt(request):
    # Récupération des données depuis la session
    session = request.session
    jobs_details = session.get('jobs_details', [])
    setup_times_str = session.get('setup_times', {})
    num_jobs = len(jobs_details)
    num_machines = session.get('num_machines', 0)

    if num_jobs == 0 or num_machines == 0:
        return render(request, 'page/error.html', {'error_message': "kkkkkkkkk."})

    # Reconversion des clés de setup_times en tuples
    setup_times = {
        tuple(map(int, key.split('_'))): value
        for key, value in setup_times_str.items()
    }

    # Tri croissant des dates d'arrivée
    if request.session.get('regle', 'Aucune règle') == "FIFO":
        # FIFO : Trier par date d'arrivée (croissant)
        jobs_details.sort(key=lambda x: int(x.get("arrival_date", 0)))

    elif request.session.get('regle', 'Aucune règle') == "LIFO":
        # LIFO : Trier par date d'arrivée (décroissant)
        jobs_details.sort(key=lambda x: int(x.get("arrival_date", 0)), reverse=True)

    elif request.session.get('regle', 'Aucune règle') == "SPT":
        # SPT : Trier par temps total de préparation (croissant)
        jobs_details.sort(
            key=lambda x: sum(machine.get("preparation_time", 0) for machine in x.get("machine_times", [])))

    elif request.session.get('regle', 'Aucune règle') == "LPT":
        # LPT : Trier par temps total de préparation (décroissant)
        jobs_details.sort(
            key=lambda x: sum(machine.get("preparation_time", 0) for machine in x.get("machine_times", [])),
            reverse=True
        )

    elif request.session.get('regle', 'Aucune règle') == "EDD":
        # EDD : Trier par date de livraison prévue (croissant)
        jobs_details.sort(key=lambda x: int(x.get("delivery_date", float('inf'))))

    else:
        # Si aucune règle n'est définie ou règle inconnue, ne pas trier
        pass


    # Initialisation des matrices de temps de début (s) et de fin (c)
    s = [[0] * num_jobs for _ in range(num_machines)]
    c = [[0] * num_jobs for _ in range(num_machines)]

    # Calcul des temps pour la première machine
    st = setup_times.get((int(jobs_details[0]["job_id"]), int(jobs_details[0]["job_id"]), 1), 0)
    s[0][0] = max(int(jobs_details[0]["arrival_date"]) ,st)
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])

    for j in range(1, num_jobs):
        sti = setup_times.get((int(jobs_details[j - 1]["job_id"]), int(jobs_details[j]["job_id"]), 1), 0)
        p = int(jobs_details[j]["machine_times"][0]["preparation_time"])
        s[0][j] = max(int(jobs_details[j]["arrival_date"]), c[0][j - 1])+sti
        c[0][j] = s[0][j] + p

    # Calcul des temps pour les autres machines
    for i in range(1, num_machines):
        sti = setup_times.get((int(jobs_details[0]["job_id"]), int(jobs_details[0]["job_id"]), i + 1), 0)
        p = int(jobs_details[0]["machine_times"][i]["preparation_time"])
        s[i][0] = max(c[i - 1][0], int(jobs_details[0]["arrival_date"]) , sti)
        c[i][0] = s[i][0] + p

        for j in range(1, num_jobs):
            sti = setup_times.get((int(jobs_details[j - 1]["job_id"]), int(jobs_details[j]["job_id"]), i + 1), 0)
            p = int(jobs_details[j]["machine_times"][i]["preparation_time"])
            s[i][j] = max(c[i - 1][j], c[i][j - 1] + sti)
            c[i][j] = s[i][j] + p


    request.session['cmax'] =c[num_machines-1][num_jobs-1]
    # Calcul des retards
    tj = []  # Liste des retards
    for i in range(num_jobs):
        # Assurez-vous que delivery_date est convertible en entier
        delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du retard pour chaque job
        tj.append(max(0, finish_time - delivery_date))

    # Calcul du total et du retard maximum
    TT = sum(tj)  # Total des retards
    Tmax = max(tj) if tj else 0  # Retard maximum, vérifiez si la liste est vide

    # Calcul des Flow Times
    ftj = []  # Liste des flow times
    for i in range(num_jobs):
        # Assurez-vous que arrival_date est convertible en entier
        arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du flow time pour chaque job
        ftj.append(finish_time - arrival_date)

    # Calcul du total des Flow Times
    Tft = sum(ftj)
    combined_data = zip(ftj, tj)
    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Ajouter les barres pour chaque tâche
    job_colors = {job["job_id"]: f"C{idx}" for idx, job in enumerate(sorted(jobs_details, key=lambda x: int(x["job_id"])))}

    for i in range(num_machines):
        for j in range(num_jobs):
            start = s[i][j]
            end = c[i][j]
            job_id = jobs_details[j]["job_id"]
            ax.barh(f"Machine {i + 1}", end - start, left=start, color=job_colors[job_id], edgecolor="black",
                    label=f"Job {job_id}" if i == 0 else "")

    # Configuration de la figure
    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - SDST")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Supprimer les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=num_jobs)

    # Enregistrer le graphique dans un buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64
    graph = base64.b64encode(image_png).decode('utf-8')

    # Rendu de la page HTML avec le graphique

    combined_data = [
        {
            "job_id": job["job_id"],
            "arrival_date": job.get("arrival_date", 0),
            "delivery_date": job.get("delivery_date", 0),
            "flow_time": flow_time,
            "retard": retard,
        }
        for job, (flow_time, retard) in zip(jobs_details, zip(ftj, tj))
    ]


    return render(request, 'page/sdst_gantt.html', {
        'graph': graph,
        'regle': request.session.get('regle', 'Aucune règle'),
        'contrainte': request.session.get('contrainte', 'Aucune contrainte'),
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,  # Liste structurée des données
        'total_flow_time': Tft,
        'total_retard': TT,
        'max_retard': Tmax,
        'cmax': request.session['cmax']
    })


def sist(request):
    num_jobs = request.session.get('num_jobs', 0)
    num_machines = request.session.get('num_machines', 0)
    jobs_details = request.session.get('jobs_details', [])

    if request.method == "POST":
        setup_times = [0] * num_machines  # Initialiser une liste de taille égale au nombre de machines

        # Collecte des temps de réglage (SIST)
        for m in range(1, num_machines + 1):
            field_name = f"setup_time_machine_{m}"  # Nom du champ du formulaire
            setup_time = int(request.POST.get(field_name, 0))
            setup_times[m - 1] = setup_time  # Assigner le temps de réglage à l'index correspondant

        # Stockage dans la session
        request.session['setup_times'] = setup_times
        return redirect('Demande')  # Redirection après soumission

    return render(request, 'page/sist.html', {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'machine_range': range(1, num_machines + 1),
    })


def sist_gantt(request):
    # Récupération des données depuis la session
    session = request.session
    jobs_details = session.get('jobs_details', [])
    num_jobs = len(jobs_details)
    num_machines = session.get('num_machines', 0)

    if num_jobs == 0 or num_machines == 0:
        return render(request, 'page/error.html', {'error_message': "Les données des tâches ou des machines sont manquantes."})

    # Reconversion des clés de setup_times en tuples
    setup_times = session.get('setup_times', [])

    # Tri croissant des dates d'arrivée
    if request.session.get('regle', 'Aucune règle') == "FIFO":
        # FIFO : Trier par date d'arrivée (croissant)
        jobs_details.sort(key=lambda x: int(x.get("arrival_date", 0)))

    elif request.session.get('regle', 'Aucune règle') == "LIFO":
        # LIFO : Trier par date d'arrivée (décroissant)
        jobs_details.sort(key=lambda x: int(x.get("arrival_date", 0)), reverse=True)

    elif request.session.get('regle', 'Aucune règle') == "SPT":
        # SPT : Trier par temps total de préparation (croissant)
        jobs_details.sort(
            key=lambda x: sum(machine.get("preparation_time", 0) for machine in x.get("machine_times", [])))

    elif request.session.get('regle', 'Aucune règle') == "LPT":
        # LPT : Trier par temps total de préparation (décroissant)
        jobs_details.sort(
            key=lambda x: sum(machine.get("preparation_time", 0) for machine in x.get("machine_times", [])),
            reverse=True
        )

    elif request.session.get('regle', 'Aucune règle') == "EDD":
        # EDD : Trier par date de livraison prévue (croissant)
        jobs_details.sort(key=lambda x: int(x.get("delivery_date", float('inf'))))

    else:
        # Si aucune règle n'est définie ou règle inconnue, ne pas trier
        pass


    # Initialisation des matrices de temps de début (s) et de fin (c)
    s = [[0] * num_jobs for _ in range(num_machines)]
    c = [[0] * num_jobs for _ in range(num_machines)]

    # Calcul des temps pour la première machine
    st = setup_times[0]
    s[0][0] = max(int(jobs_details[0]["arrival_date"]) ,st)
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])

    for j in range(1, num_jobs):
        st = setup_times[0]
        p = int(jobs_details[j]["machine_times"][0]["preparation_time"])
        s[0][j] = max(int(jobs_details[j]["arrival_date"]), c[0][j - 1]) + st
        c[0][j] = s[0][j] + p

    # Calcul des temps pour les autres machines
    for i in range(1, num_machines):
        st = setup_times[0]
        p = int(jobs_details[0]["machine_times"][i]["preparation_time"])
        s[i][0] = max(c[i - 1][0], int(jobs_details[0]["arrival_date"]), st)
        c[i][0] = s[i][0] + p

        for j in range(1, num_jobs):
            st = setup_times[i]
            p = int(jobs_details[j]["machine_times"][i]["preparation_time"])
            s[i][j] = max(c[i - 1][j], c[i][j - 1] + st)
            c[i][j] = s[i][j] + p
    request.session['cmax'] = c[num_machines - 1][num_jobs - 1]
    # Calcul des retards
    tj = []  # Liste des retards
    for i in range(num_jobs):
        # Assurez-vous que delivery_date est convertible en entier
        delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du retard pour chaque job
        tj.append(max(0, finish_time - delivery_date))

    # Calcul du total et du retard maximum
    TT = sum(tj)  # Total des retards
    Tmax = max(tj) if tj else 0  # Retard maximum, vérifiez si la liste est vide

    # Calcul des Flow Times
    ftj = []  # Liste des flow times
    for i in range(num_jobs):
        # Assurez-vous que arrival_date est convertible en entier
        arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du flow time pour chaque job
        ftj.append(finish_time - arrival_date)

    # Calcul du total des Flow Times
    Tft = sum(ftj)
    combined_data = zip(ftj, tj)
    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Ajouter les barres pour chaque tâche
    job_colors = {job["job_id"]: f"C{idx}" for idx, job in enumerate(sorted(jobs_details, key=lambda x: int(x["job_id"])))}

    for i in range(num_machines):
        for j in range(num_jobs):
            start = s[i][j]
            end = c[i][j]
            job_id = jobs_details[j]["job_id"]
            ax.barh(f"Machine {i + 1}", end - start, left=start, color=job_colors[job_id], edgecolor="black",
                    label=f"Job {job_id}" if i == 0 else "")

    # Configuration de la figure
    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - SDST")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Supprimer les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=num_jobs)

    # Enregistrer le graphique dans un buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64
    graph = base64.b64encode(image_png).decode('utf-8')

    # Rendu de la page HTML avec le graphique

    combined_data = [
        {
            "job_id": job["job_id"],
            "arrival_date": job.get("arrival_date", 0),
            "delivery_date": job.get("delivery_date", 0),
            "flow_time": flow_time,
            "retard": retard,
        }
        for job, (flow_time, retard) in zip(jobs_details, zip(ftj, tj))
    ]

    return render(request, 'page/sdst_gantt.html', {
        'graph': graph,
        'regle': request.session.get('regle', 'Aucune règle'),
        'contrainte': request.session.get('contrainte', 'Aucune contrainte'),
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,  # Liste structurée des données
        'total_flow_time': Tft,
        'total_retard': TT,
        'max_retard': Tmax,
        'cmax': request.session['cmax']
    })


import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render


def no_wait(request):
    session = request.session
    jobs_details = session.get('jobs_details', [])

    # Application de la règle de priorité choisie par l'utilisateur
    if session.get('regle', 'Aucune règle') == "FIFO":
        jobs_details.sort(key=lambda x: int(x["arrival_date"]))
    elif session.get('regle', 'Aucune règle') == "LIFO":
        jobs_details.sort(key=lambda x: int(x["arrival_date"]), reverse=True)
    elif session.get('regle', 'Aucune règle') == "SPT":
        jobs_details.sort(key=lambda x: sum(int(machine["preparation_time"]) for machine in x["machine_times"]))
    elif session.get('regle', 'Aucune règle') == "LPT":
        jobs_details.sort(key=lambda x: sum(int(machine["preparation_time"]) for machine in x["machine_times"]),
                          reverse=True)
    elif session.get('regle', 'Aucune règle') == "EDD":
        jobs_details.sort(key=lambda x: int(x["delivery_date"]))

    # Convertir les nombres de la session de str à int
    m = int(session['num_machines'])
    n = int(session['num_jobs'])

    s = [[0] * n for _ in range(m)]  # Temps de début pour chaque tâche
    c = [[0] * n for _ in range(m)]  # Temps de fin pour chaque tâche
    a = [0] * n

    # Initialisation des temps pour la première machine et la première tâche
    s[0][0] = int(jobs_details[0]["arrival_date"])  # Conversion en entier
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])
    for i in range(m):
        a[0] += int(jobs_details[0]["machine_times"][i]["preparation_time"])

    for i in range(1, n):
        l = []
        v = 0
        for d in range(m):
            k = d
            for j in range(k, m):
                v += int(jobs_details[i]["machine_times"][j]["preparation_time"]) - \
                     int(jobs_details[i - 1]["machine_times"][j]["preparation_time"])
            v += int(jobs_details[i - 1]["machine_times"][d]["preparation_time"])
            l.append(v)
            v = 0
        a[i] = max(l)

    c[m - 1][0] = a[0]
    for i in range(1, n):
        c[m - 1][i] = a[i] + c[m - 1][i - 1]

    for i in range(m - 2, -1, -1):
        for j in range(n):
            c[i][j] = c[i + 1][j] - int(jobs_details[j]["machine_times"][i + 1]["preparation_time"])

    for i in range(m):
        for j in range(n):
            s[i][j] = c[i][j] - int(jobs_details[j]["machine_times"][i]["preparation_time"])

    s[0][0] = 0

    for i in range(m):
        for j in range(n):
            s[i][j] += int(jobs_details[0]["arrival_date"])
            c[i][j] += int(jobs_details[0]["arrival_date"])

    for j in range(1, n):
        if s[0][j] < int(jobs_details[j]["arrival_date"]):
            d = int(jobs_details[j]["arrival_date"]) - s[0][j]

            for k in range(j, n):
                for i in range(m):
                    s[i][k] += d
                    c[i][k] += d
    num_machines=m
    num_jobs=n
    # Calcul du Cmax et stockage dans la session
    request.session['cmax'] = c[m - 1][n - 1]
    request.session['cmax'] = c[num_machines - 1][num_jobs - 1]
    # Calcul des retards
    tj = []  # Liste des retards
    for i in range(num_jobs):
        # Assurez-vous que delivery_date est convertible en entier
        delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du retard pour chaque job
        tj.append(max(0, finish_time - delivery_date))

    # Calcul du total et du retard maximum
    TT = sum(tj)  # Total des retards
    Tmax = max(tj) if tj else 0  # Retard maximum, vérifiez si la liste est vide

    # Calcul des Flow Times
    ftj = []  # Liste des flow times
    for i in range(num_jobs):
        # Assurez-vous que arrival_date est convertible en entier
        arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du flow time pour chaque job
        ftj.append(finish_time - arrival_date)

    # Calcul du total des Flow Times
    Tft = sum(ftj)
    combined_data = zip(ftj, tj)
    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Créer un dictionnaire de couleurs fixes pour chaque job_id
    job_colors = {job["job_id"]: f"C{idx}" for idx, job in
                  enumerate(sorted(jobs_details, key=lambda x: int(x["job_id"])))}

    # Affichage des barres du diagramme de Gantt
    for i in range(m):
        for j in range(n):
            start = s[i][j]
            end = c[i][j]
            k = jobs_details[j]["job_id"]
            ax.barh(f"Machine {i + 1}",
                    end - start,
                    left=start,
                    color=job_colors[k],
                    edgecolor="black",
                    label=f"{k}" if i == 0 else "")

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - No-Wait")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Supprimer les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    # Trier les légendes par job_id
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: int(x[1]))
    handles, labels = zip(*sorted_pairs)
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=n)

    # Enregistrer le graphique dans un buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64 pour l'affichage dans la page
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')

    # Rendu de la vue avec le graphique et les autres informations

    combined_data = [
        {
            "job_id": job["job_id"],
            "arrival_date": job.get("arrival_date", 0),
            "delivery_date": job.get("delivery_date", 0),
            "flow_time": flow_time,
            "retard": retard,
        }
        for job, (flow_time, retard) in zip(jobs_details, zip(ftj, tj))
    ]


    return render(request, 'page/No-Wait.html', {
        'graph': graph,
        'regle': request.session.get('regle', 'Aucune règle'),
        'contrainte': request.session.get('contrainte', 'Aucune contrainte'),
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,  # Liste structurée des données
        'total_flow_time': Tft,
        'total_retard': TT,
        'max_retard': Tmax,
        'cmax': request.session['cmax']
    })


import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render


import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render


import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib.pyplot as plt
import io
import base64

import matplotlib.pyplot as plt
import io
import base64

import matplotlib.pyplot as plt
import io
import base64


def no_idle(request):
    session = request.session
    jobs_details = session.get('jobs_details', [])

    # Application de la règle de priorité choisie par l'utilisateur
    if session.get('regle', 'Aucune règle') == "FIFO":
        jobs_details.sort(key=lambda x: int(x["arrival_date"]))
    elif session.get('regle', 'Aucune règle') == "LIFO":
        jobs_details.sort(key=lambda x: int(x["arrival_date"]), reverse=True)
    elif session.get('regle', 'Aucune règle') == "SPT":
        jobs_details.sort(key=lambda x: sum(int(machine["preparation_time"]) for machine in x["machine_times"]))
    elif session.get('regle', 'Aucune règle') == "LPT":
        jobs_details.sort(key=lambda x: sum(int(machine["preparation_time"]) for machine in x["machine_times"]),
                          reverse=True)
    elif session.get('regle', 'Aucune règle') == "EDD":
        jobs_details.sort(key=lambda x: int(x["delivery_date"]))

    # Convertir les nombres de la session de str à int
    m = int(session['num_machines'])
    n = int(session['num_jobs'])

    # Initialisation
    m = int(session['num_machines'])  # Nombre de machines
    n = int(session['num_jobs'])  # Nombre de jobs
    l = [0] * m  # Initialisation de L

    # Calcul des L_i
    for i in range(1, m):  # Pour chaque machine (i=2,...,m)
        d = [0] * n
        for k in range(n):  # Pour chaque
            s1 = 0
            s2 = 0
            for j in range(k + 1):  # Somme des temps de préparation pour machine i
                s1 += int(jobs_details[j]["machine_times"][i - 1]["preparation_time"])
            for j in range(k):  # Somme des temps de préparation pour machine (i-1)
                s2 += int(jobs_details[j]["machine_times"][i]["preparation_time"])
            d[k] = s1 - s2  # Différence entre les deux sommes
        print(d)
        l[i] = l[i - 1] + max(d)  # Mise

    # Résultat
    s = [[0] * n for _ in range(m)]
    c = [[0] * n for _ in range(m)]
    s[0][0] = 0
    c[0][0] = s[0][0] + int(session['jobs_details'][0]["machine_times"][0]["preparation_time"])  # Conversion en entier

    # Calcul des temps pour la première machine

    # Calcul des temps pour les autres machines
    for i in range(m):
        p = int(session['jobs_details'][0]["machine_times"][i]["preparation_time"])  # Conversion en entier
        s[i][0] = l[i]
        c[i][0] = s[i][0] + p
    for j in range(1, n):
        for i in range(m):
            p = int(session['jobs_details'][j]["machine_times"][i]["preparation_time"])
            s[i][j] = c[i][j - 1]
            c[i][j] = s[i][j] + p
    for j in range(n):

        if s[0][j] < int(jobs_details[j]["arrival_date"]):
            v = int(jobs_details[j]["arrival_date"]) - s[0][j]
            for i in range(m):
                for j in range(n):
                    s[i][j] = s[i][j] + v
                    c[i][j] = c[i][j] + v

    num_machines = m
    num_jobs = n
    # Calcul du Cmax et stockage dans la session
    request.session['cmax'] = c[m - 1][n - 1]
    request.session['cmax'] = c[num_machines - 1][num_jobs - 1]
    # Calcul des retards
    tj = []  # Liste des retards
    for i in range(num_jobs):
        # Assurez-vous que delivery_date est convertible en entier
        delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du retard pour chaque job
        tj.append(max(0, finish_time - delivery_date))

    # Calcul du total et du retard maximum
    TT = sum(tj)  # Total des retards
    Tmax = max(tj) if tj else 0  # Retard maximum, vérifiez si la liste est vide

    # Calcul des Flow Times
    ftj = []  # Liste des flow times
    for i in range(num_jobs):
        # Assurez-vous que arrival_date est convertible en entier
        arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
        finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
        # Calcul du flow time pour chaque job
        ftj.append(finish_time - arrival_date)

    # Calcul du total des Flow Times
    Tft = sum(ftj)
    combined_data = zip(ftj, tj)
    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Créer un dictionnaire de couleurs fixes pour chaque job_id
    job_colors = {job["job_id"]: f"C{idx}" for idx, job in
                  enumerate(sorted(jobs_details, key=lambda x: int(x["job_id"])))}

    # Affichage des barres du diagramme de Gantt
    for i in range(m):
        for j in range(n):
            start = s[i][j]
            end = c[i][j]
            k = jobs_details[j]["job_id"]
            ax.barh(f"Machine {i + 1}",
                    end - start,
                    left=start,
                    color=job_colors[k],
                    edgecolor="black",
                    label=f"{k}" if i == 0 else "")

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - No-Wait")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Supprimer les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    # Trier les légendes par job_id
    sorted_pairs = sorted(zip(handles, labels), key=lambda x: int(x[1]))
    handles, labels = zip(*sorted_pairs)
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=n)

    # Enregistrer le graphique dans un buffer
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64 pour l'affichage dans la page
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')

    # Rendu de la vue avec le graphique et les autres informations

    combined_data = [
        {
            "job_id": job["job_id"],
            "arrival_date": job.get("arrival_date", 0),
            "delivery_date": job.get("delivery_date", 0),
            "flow_time": flow_time,
            "retard": retard,
        }
        for job, (flow_time, retard) in zip(jobs_details, zip(ftj, tj))
    ]

    return render(request, 'page/no_idle.html', {
        'graph': graph,
        'regle': request.session.get('regle', 'Aucune règle'),
        'contrainte': request.session.get('contrainte', 'Aucune contrainte'),
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,  # Liste structurée des données
        'total_flow_time': Tft,
        'total_retard': TT,
        'max_retard': Tmax,
        'cmax': request.session['cmax']
    })


def probleme_optimisation(request):
    if request.method == "POST":
        # Récupération des données du formulaire
        num_jobs = int(request.POST.get('num_jobs', 0))
        num_machines = int(request.POST.get('num_machines', 0))

        # Limitation du nombre de jobs à 10
        num_jobs = min(num_jobs, 10)

        # Stockage des données dans la session
        request.session['num_jobs'] = num_jobs
        request.session['num_machines'] = num_machines

        # Redirection vers la page suivante
        return redirect('jobsdetail')  # Par exemple, vers un formulaire pour saisir les détails des jobs et machines

    return render(request, 'page/probleme_optimisation.html')


import matplotlib.pyplot as plt
from copy import deepcopy

import matplotlib.pyplot as plt
import io
import base64
from copy import deepcopy
from django.shortcuts import render
from django.http import HttpResponse
import io
import base64
import matplotlib.pyplot as plt

from copy import deepcopy
from django.shortcuts import render
from django.http import HttpResponse
import io
import base64
import matplotlib.pyplot as plt

def makespan(session):
    m = session['num_machines']
    n = session['num_jobs']
    s = [[0] * n for _ in range(m)]
    c = [[0] * n for _ in range(m)]


    s[0][0] = int(session['jobs_details'][0]["arrival_date"])
    c[0][0] = s[0][0] + int(session['jobs_details'][0]["machine_times"][0]["preparation_time"])  # Conversion en entier

    # Calcul des temps pour la première machine
    for i in range(1, n):
        p = int(session['jobs_details'][i]["machine_times"][0]["preparation_time"])  # Conversion en entier
        s[0][i] = max(int(session['jobs_details'][i]["arrival_date"]), c[0][i - 1])  # Conversion en entier
        c[0][i] = s[0][i] + p

    # Calcul des temps pour les autres machines
    for i in range(1, m):
        p = int(session['jobs_details'][0]["machine_times"][i]["preparation_time"])  # Conversion en entier
        s[i][0] = max(c[i - 1][0], int(session['jobs_details'][0]["arrival_date"]))  # Conversion en entier
        c[i][0] = s[i][0] + p
        for j in range(1, n):
            p = int(session['jobs_details'][j]["machine_times"][i]["preparation_time"])  # Conversion en entier
            s[i][j] = max(c[i - 1][j], c[i][j - 1])
            c[i][j] = s[i][j] + p

    cmax = c[m - 1][n - 1]
    return [cmax, c, s]

from itertools import permutations
from copy import deepcopy

import matplotlib.pyplot as plt
from copy import deepcopy

def makespanSIST(session):
    """
    Calcule le makespan pour une session avec des temps de préparation (setup times) entre les machines.
    Les types des variables sont explicitement convertis en entiers pour éviter les erreurs.
    """
    m = int(session['num_machines'])  # Nombre de machines
    n = int(session['num_jobs'])      # Nombre de tâches
    s = [[0] * n for _ in range(m)]   # Temps de début pour chaque tâche
    c = [[0] * n for _ in range(m)]   # Temps de fin pour chaque tâche
    setup_times = [int(x) for x in session.get('setup_times', [0] * m)]  # Conversion des temps de setup en entier

    # Initialisation des temps pour la première machine et la première tâche
    s[0][0] = max(int(session['jobs_details'][0]["arrival_date"]), setup_times[0])
    c[0][0] = s[0][0] + int(session['jobs_details'][0]["machine_times"][0]["preparation_time"])

    # Calcul des temps pour la première machine
    for j in range(1, n):
        p = int(session['jobs_details'][j]["machine_times"][0]["preparation_time"])  # Temps de préparation
        s[0][j] = max(c[0][j - 1] + setup_times[0], int(session['jobs_details'][j]["arrival_date"]))  # Temps de début
        c[0][j] = s[0][j] + p  # Temps de fin

    # Calcul des temps pour les autres machines
    for i in range(1, m):
        for j in range(n):
            p = int(session['jobs_details'][j]["machine_times"][i]["preparation_time"])  # Temps de préparation
            st = setup_times[i]  # Temps de setup
            if j == 0:
                # Calcul pour la première tâche sur la machine courante
                s[i][j] = max(c[i - 1][j] ,st, int(session['jobs_details'][j]["arrival_date"]))
            else:
                # Calcul pour les autres tâches
                s[i][j] = max(c[i - 1][j], c[i][j - 1] + st)
            c[i][j] = s[i][j] + p  # Temps de fin

    # Calcul du makespan
    cmax = c[m - 1][n - 1]
    return [cmax, c, s]

def makespanSDST(session ):
    # Récupération des données depuis la session

    jobs_details = session.get('jobs_details', [])
    setup_times_str = session.get('setup_times', {})
    num_jobs = len(jobs_details)
    num_machines = session.get('num_machines', 0)

    # Vérifications initiales

    # Reconversion des clés de setup_times en tuples
    setup_times = {
        tuple(map(int, key.split('_'))): int(value)
        for key, value in setup_times_str.items()
    }

    # Initialisation des matrices
    s = [[0] * num_jobs for _ in range(num_machines)]  # Temps de début
    c = [[0] * num_jobs for _ in range(num_machines)]  # Temps de fin

    # Calcul des temps pour la première machine
    sti = setup_times.get((int(jobs_details[0]["job_id"]), int(jobs_details[0]["job_id"]), 1), 0)
    s[0][0] = max(int(jobs_details[0]["arrival_date"]), sti)
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])

    for j in range(1, num_jobs):
        sti = setup_times.get((int(jobs_details[j - 1]["job_id"]), int(jobs_details[j]["job_id"]), 1), 0)
        p = int(jobs_details[j]["machine_times"][0]["preparation_time"])
        s[0][j] = max(c[0][j - 1] + sti, int(jobs_details[j]["arrival_date"]))
        c[0][j] = s[0][j] + p

    # Calcul des temps pour les autres machines
    for i in range(1, num_machines):
        sti = setup_times.get((int(jobs_details[0]["job_id"]), int(jobs_details[0]["job_id"]), i + 1), 0)
        p = int(jobs_details[0]["machine_times"][i]["preparation_time"])
        s[i][0] = max(c[i - 1][0] + sti, int(jobs_details[0]["arrival_date"]))
        c[i][0] = s[i][0] + p

        for j in range(1, num_jobs):
            sti = setup_times.get((int(jobs_details[j - 1]["job_id"]), int(jobs_details[j]["job_id"]), i + 1), 0)
            p = int(jobs_details[j]["machine_times"][i]["preparation_time"])
            s[i][j] = max(c[i - 1][j], c[i][j - 1] + sti)
            c[i][j] = s[i][j] + p

    # Calcul du makespan
    cmax = c[num_machines - 1][num_jobs - 1]
    return [cmax, c, s]

def makespanNowait(session):
    jobs_details = session.get('jobs_details', [])
    m = int(session['num_machines'])
    n = int(session['num_jobs'])

    s = [[0] * n for _ in range(m)]  # Temps de début pour chaque tâche
    c = [[0] * n for _ in range(m)]  # Temps de fin pour chaque tâche
    a = [0] * n

    # Initialisation des temps pour la première machine et la première tâche
    s[0][0] = int(jobs_details[0]["arrival_date"])  # Conversion en entier
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])
    for i in range(m):
        a[0] += int(jobs_details[0]["machine_times"][i]["preparation_time"])

    for i in range(1, n):
        l = []
        v = 0
        for d in range(m):
            k = d
            for j in range(k, m):
                v += int(jobs_details[i]["machine_times"][j]["preparation_time"]) - \
                     int(jobs_details[i - 1]["machine_times"][j]["preparation_time"])
            v += int(jobs_details[i - 1]["machine_times"][d]["preparation_time"])
            l.append(v)
            v = 0
        a[i] = max(l)

    c[m - 1][0] = a[0]
    for i in range(1, n):
        c[m - 1][i] = a[i] + c[m - 1][i - 1]

    for i in range(m - 2, -1, -1):
        for j in range(n):
            c[i][j] = c[i + 1][j] - int(jobs_details[j]["machine_times"][i + 1]["preparation_time"])

    for i in range(m):
        for j in range(n):
            s[i][j] = c[i][j] - int(jobs_details[j]["machine_times"][i]["preparation_time"])

    s[0][0] = 0

    for i in range(m):
        for j in range(n):
            s[i][j] += int(jobs_details[0]["arrival_date"])
            c[i][j] += int(jobs_details[0]["arrival_date"])

    for j in range(1, n):
        if s[0][j] < int(jobs_details[j]["arrival_date"]):
            d = int(jobs_details[j]["arrival_date"]) - s[0][j]

            for k in range(j, n):
                for i in range(m):
                    s[i][k] += d
                    c[i][k] += d

    # Calcul du Cmax et stockage dans la session
    cmax = c[m - 1][n- 1]
    return [cmax, c, s]

def solution_optimale(session):
    """
    Trouve la séquence optimale pour minimiser le makespan en testant toutes les permutations possibles.
    """
    c_optimale = float('inf')  # Initialise le makespan optimal à un très grand nombre
    sequence_optimale = None  # Variable pour stocker la meilleure séquence trouvée

    # Génère toutes les permutations des tâches
    for perm in permutations(session['jobs_details']):
        # Crée une copie de la session pour tester cette permutation
        session_test = deepcopy(session)
        session_test['jobs_details'] = list(perm)  # Remplace l'ordre des tâches par la permutation actuelle
        if session['contrainte'] == "SDST":
            cmax, _, _ = makespanSDST(session_test)
        elif  session['contrainte'] == "SIST":
           cmax,_,_ = makespanSIST(session_test)
        elif session['contrainte'] == "No wait":
           cmax, _, _ = makespanNowait(session_test)
        # Calcule le makespan pour cette séquence
        else:
           cmax, _, _ = makespan(session_test)

        # Met à jour la solution optimale si on trouve une meilleure séquence
        if cmax < c_optimale:
            c_optimale = cmax
            sequence_optimale = deepcopy(session_test)

    return sequence_optimale





def optimisation(request):
    try:
        # Vérification des données nécessaires dans la session
        if not all(key in request.session for key in ['jobs_details', 'num_jobs', 'num_machines']):
            return HttpResponse("Données insuffisantes dans la session.", status=400)

        session = request.session
        session_optimale = solution_optimale(session)

        # Choix de la contrainte
        contrainte = session.get('contrainte', 'Aucune contrainte')
        if contrainte == "SDST":
            cmax, c, s = makespanSIST(session_optimale)
        elif contrainte == "SIST":
            cmax, c, s = makespanSIST(session_optimale)
        elif contrainte == "No wait":
            cmax, c, s = makespanNowait(session_optimale)
        else:
            cmax, c, s = makespan(session_optimale)

        # Récupération des détails des jobs
        jobs_details = session.get('jobs_details', [])
        num_jobs = session.get('num_jobs', 0)
        num_machines = session.get('num_machines', 0)

        # Calcul des retards (Tardiness)
        tardiness = []  # Liste des retards
        for i in range(num_jobs):
            delivery_date = int(jobs_details[i].get("delivery_date", 0))  # Valeur par défaut 0 si absente
            finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
            tardiness.append(max(0, finish_time - delivery_date))

        # Calcul du total et du retard maximal
        total_tardiness = sum(tardiness)
        max_tardiness = max(tardiness) if tardiness else 0

        # Calcul des Flow Times
        flow_times = []  # Liste des flow times
        for i in range(num_jobs):
            arrival_date = int(jobs_details[i].get("arrival_date", 0))  # Valeur par défaut 0 si absente
            finish_time = c[num_machines - 1][i]  # Temps de fin du job sur la dernière machine
            flow_times.append(finish_time - arrival_date)

        # Calcul du Flow Time total
        total_flow_time = sum(flow_times)

        # Combiner les données des jobs, flow times, et retards
        combined_data = [
            {
                "job_id": job.get("job_id", "N/A"),
                "arrival_date": job.get("arrival_date", "N/A"),
                "delivery_date": job.get("delivery_date", "N/A"),
                "flow_time": flow_time,
                "tardiness": tardiness_val
            }
            for job, flow_time, tardiness_val in zip(jobs_details, flow_times, tardiness)
        ]

        # Création du diagramme de Gantt
        job_colors = {str(job["job_id"]): f"C{index}" for index, job in enumerate(session_optimale['jobs_details'])}
        fig, ax = plt.subplots(figsize=(10, 6))

        for i in range(num_machines):
            for j in range(num_jobs):
                start = s[i][j]
                end = c[i][j]
                job_id = str(session_optimale['jobs_details'][j]["job_id"])  # Conversion explicite
                ax.barh(f"Machine {i + 1}",
                        end - start,
                        left=start,
                        color=job_colors[job_id],
                        edgecolor="black",
                        label=f"Tâche {job_id}" if i == 0 else "")

        ax.set_xlabel("Temps")
        ax.set_ylabel("Machines")
        ax.set_title("Diagramme de Gantt - Séquence Optimale")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # Supprimer les doublons dans la légende
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))
        ax.legend(unique_labels.values(), unique_labels.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=num_jobs)

        # Enregistrer le graphique en base64
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graph = base64.b64encode(image_png).decode('utf-8')

        # Rendu avec les informations nécessaires
        return render(request, 'page/optimisation.html', {
            'graph': graph,
            'contrainte': contrainte,
            'num_jobs': num_jobs,
            'num_machines': num_machines,
            'cmax': cmax,
            'total_flow_time': total_flow_time,
            'total_tardiness': total_tardiness,
            'max_tardiness': max_tardiness,
            'combined_data': combined_data  # Liste structurée des données
        })

    except Exception as e:
        return HttpResponse(f"Erreur interne : {e}", status=500)



import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.http import HttpResponse

def TAR(request):
    session = request.session
    m = session['num_machines']
    n = session['num_jobs']

    # Initialisation
    tempsFonctionnementMachine = [0] * m
    TauxFonctionnementMachine = [0] * m
    TauxsArretMachine = [0] * m

    # Calcul des temps de fonctionnement pour chaque machine
    for i in range(n):
        for j in range(m):
            tempsFonctionnementMachine[j] += session['jobs_details'][i]["machine_times"][j]["preparation_time"]

    # Calcul des taux de fonctionnement et d'arrêt
    for i in range(m):
        TauxFonctionnementMachine[i] = 100 * (tempsFonctionnementMachine[i] / session['cmax'])
        TauxsArretMachine[i] = 100 - TauxFonctionnementMachine[i]

    # Création de l'histogramme
    machines = [f"Machine {i+1}" for i in range(m)]
    x = range(len(machines))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.bar(x, TauxFonctionnementMachine, width=width, label="Taux de Fonctionnement", color='blue', alpha=0.7)
    plt.bar([i + width for i in x], TauxsArretMachine, width=width, label="Taux d'Arrêt", color='orange', alpha=0.7)

    plt.xlabel("Machines")
    plt.ylabel("Pourcentage (%)")
    plt.title("Taux de Fonctionnement et d'Arrêt des Machines")
    plt.xticks([i + width / 2 for i in x], machines)
    plt.legend()

    # Sauvegarder le graphique dans un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encoder l'image en base64
    graphic = base64.b64encode(image_png).decode('utf-8')

    # Retourner le template avec l'image encodée
    return render(request, 'page/tar.html', {'graphic': graphic})

def makespanNowait(session):
    jobs_details = session.get('jobs_details', [])
    m = int(session['num_machines'])
    n = int(session['num_jobs'])

    s = [[0] * n for _ in range(m)]  # Temps de début pour chaque tâche
    c = [[0] * n for _ in range(m)]  # Temps de fin pour chaque tâche
    a = [0] * n

    # Initialisation des temps pour la première machine et la première tâche
    s[0][0] = int(jobs_details[0]["arrival_date"])  # Conversion en entier
    c[0][0] = s[0][0] + int(jobs_details[0]["machine_times"][0]["preparation_time"])
    for i in range(m):
        a[0] += int(jobs_details[0]["machine_times"][i]["preparation_time"])

    for i in range(1, n):
        l = []
        v = 0
        for d in range(m):
            k = d
            for j in range(k, m):
                v += int(jobs_details[i]["machine_times"][j]["preparation_time"]) - \
                     int(jobs_details[i - 1]["machine_times"][j]["preparation_time"])
            v += int(jobs_details[i - 1]["machine_times"][d]["preparation_time"])
            l.append(v)
            v = 0
        a[i] = max(l)

    c[m - 1][0] = a[0]
    for i in range(1, n):
        c[m - 1][i] = a[i] + c[m - 1][i - 1]

    for i in range(m - 2, -1, -1):
        for j in range(n):
            c[i][j] = c[i + 1][j] - int(jobs_details[j]["machine_times"][i + 1]["preparation_time"])

    for i in range(m):
        for j in range(n):
            s[i][j] = c[i][j] - int(jobs_details[j]["machine_times"][i]["preparation_time"])

    s[0][0] = 0

    for i in range(m):
        for j in range(n):
            s[i][j] += int(jobs_details[0]["arrival_date"])
            c[i][j] += int(jobs_details[0]["arrival_date"])

    for j in range(1, n):
        if s[0][j] < int(jobs_details[j]["arrival_date"]):
            d = int(jobs_details[j]["arrival_date"]) - s[0][j]

            for k in range(j, n):
                for i in range(m):
                    s[i][k] += d
                    c[i][k] += d

    # Calcul du Cmax et stockage dans la session
    cmax = c[m - 1][n- 1]
    return [cmax, c, s]

def ateliersinjobshop(request):
    if request.method == "POST":
        # Récupérer la contrainte sélectionnée
        selected_atelier = request.POST.get('atelierjobshop')


        # Enregistrer la règle dans la session
        request.session['regle'] = selected_atelier

        # Enregistrer dans la session
        request.session['atelierjobshop'] = selected_atelier

        # Ajouter un drapeau pour réinitialiser les données dans saisie_classe_12
        request.session['reset_jobs_C12'] = True
        request.session['reset_jobs_C1'] = True
        request.session['reset_jobs_C21'] = True
        request.session['reset_jobs_C2'] = True
        if selected_atelier == "Atelier a deux machine":
            return redirect('saisie_classe_1')
        else:
            return redirect('probleme2')

    return render(request, 'page/atelierjobshop.html')



def saisie_classe_12(request):
    # Réinitialiser les données si le drapeau est présent
    if request.session.get('reset_jobs_C12', False):
        request.session["jobs_C12"] = []  # Réinitialiser les données
        request.session.pop('reset_jobs_C12')  # Supprimer le drapeau après réinitialisation

    # Assurez-vous que la clé existe dans la session
    if "jobs_C12" not in request.session:
        request.session["jobs_C12"] = []

    jobs_data = request.session["jobs_C12"]

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        machine_time_1 = request.POST.get("machine_time_1")
        machine_time_2 = request.POST.get("machine_time_2")

        if not job_id or not machine_time_1 or not machine_time_2:
            return HttpResponse("Veuillez remplir tous les champs.", status=400)

        try:
            job_id = int(job_id)
            machine_time_1 = int(machine_time_1)
            machine_time_2 = int(machine_time_2)
        except ValueError:
            return HttpResponse("Les champs doivent être des nombres.", status=400)

        # Ajouter un nouveau job
        new_job = {"job_id": job_id, "machine_times": [machine_time_1, machine_time_2]}
        jobs_data.append(new_job)

        # Sauvegarder les modifications
        request.session["jobs_C12"] = jobs_data
        request.session.modified = True

        return redirect("saisie_classe_12")

    return render(request, "page/saisie_classe_12.html", {
        "jobs_C12": jobs_data
    })

from django.shortcuts import render, redirect
from django.http import HttpResponse

def saisie_classe_1(request):
    # Réinitialiser les données si le drapeau est présent
    if request.session.get('reset_jobs_C1', False):
        request.session["jobs_C1"] = []  # Réinitialiser les données
        request.session.pop('reset_jobs_C1')  # Supprimer le drapeau après réinitialisation

    # Assurez-vous que la clé existe dans la session
    if "jobs_C1" not in request.session:
        request.session["jobs_C1"] = []

    jobs_data = request.session["jobs_C1"]

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        machine_time_1 = request.POST.get("machine_time_1")

        # Validation des champs
        if not job_id or not machine_time_1:
            return HttpResponse("Veuillez remplir tous les champs.", status=400)

        try:
            job_id = int(job_id)
            machine_time_1 = int(machine_time_1)
        except ValueError:
            return HttpResponse("Les champs doivent être des nombres valides.", status=400)

        # Ajouter un nouveau job
        new_job = {"job_id": job_id, "machine_times": [machine_time_1, 0]}  # Machine 2 = 0 pour C1
        jobs_data.append(new_job)

        # Sauvegarder les modifications
        request.session["jobs_C1"] = jobs_data
        request.session.modified = True

        return redirect("saisie_classe_1")

    return render(request, "page/saisie_classe_1.html", {
        "jobs_C1": jobs_data
    })


def saisie_classe_21(request):
    # Réinitialiser les données si le drapeau est présent
    if request.session.get('reset_jobs_C21', False):
        request.session["jobs_C21"] = []  # Réinitialiser les données
        request.session.pop('reset_jobs_C21')  # Supprimer le drapeau après réinitialisation

    # Assurez-vous que la clé existe dans la session
    if "jobs_C21" not in request.session:
        request.session["jobs_C21"] = []

    jobs_data = request.session["jobs_C21"]

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        machine_time_1 = request.POST.get("machine_time_1")
        machine_time_2 = request.POST.get("machine_time_2")

        # Validation des champs
        if not job_id or not machine_time_1 or not machine_time_2:
            return HttpResponse("Veuillez remplir tous les champs.", status=400)

        try:
            job_id = int(job_id)
            machine_time_1 = int(machine_time_1)
            machine_time_2 = int(machine_time_2)
        except ValueError:
            return HttpResponse("Les champs doivent être des nombres valides.", status=400)

        # Ajouter un nouveau job
        new_job = {"job_id": job_id, "machine_times": [machine_time_1, machine_time_2]}
        jobs_data.append(new_job)

        # Sauvegarder les modifications
        request.session["jobs_C21"] = jobs_data
        request.session.modified = True

        return redirect("saisie_classe_21")

    return render(request, "page/saisie_classe_21.html", {
        "jobs_C21": jobs_data
    })

def saisie_classe_2(request):
    # Réinitialiser les données si le drapeau est présent
    if request.session.get('reset_jobs_C2', False):
        request.session["jobs_C2"] = []  # Réinitialiser les données
        request.session.pop('reset_jobs_C2')  # Supprimer le drapeau après réinitialisation

    # Assurez-vous que la clé existe dans la session
    if "jobs_C2" not in request.session:
        request.session["jobs_C2"] = []

    jobs_data = request.session["jobs_C2"]

    if request.method == "POST":
        job_id = request.POST.get("job_id")
        machine_time_2 = request.POST.get("machine_time_2")

        # Validation des champs
        if not job_id or not machine_time_2:
            return HttpResponse("Veuillez remplir tous les champs.", status=400)

        try:
            job_id = int(job_id)
            machine_time_2 = int(machine_time_2)
        except ValueError:
            return HttpResponse("Les champs doivent être des nombres valides.", status=400)

        # Ajouter un nouveau job
        new_job = {"job_id": job_id, "machine_times": [0, machine_time_2]}  # Machine 1 = 0 pour C2
        jobs_data.append(new_job)

        # Sauvegarder les modifications
        request.session["jobs_C2"] = jobs_data
        request.session.modified = True

        return redirect("saisie_classe_2")

    return render(request, "page/saisie_classe_2.html", {
        "jobs_C2": jobs_data
    })

def saisie_jobs(request, class_type):
    valid_classes = ["C12", "C21", "C1", "C2"]

    # Vérifier si la classe est valide
    if class_type not in valid_classes:
        return HttpResponse("Classe invalide", status=400)

    # Initialisation des jobs dans la session si nécessaire
    if "jobs" not in request.session:
        request.session["jobs"] = {cls: [] for cls in valid_classes}

    jobs_data = request.session["jobs"]

    if request.method == "POST":
        # Récupérer les données du formulaire
        job_id = int(request.POST.get("job_id"))
        machine_time_1 = int(request.POST.get("machine_time_1", 0))
        machine_time_2 = int(request.POST.get("machine_time_2", 0))

        # Ajouter le job à la classe correspondante
        job = {"job_id": job_id, "machine_times": [machine_time_1, machine_time_2]}
        jobs_data[class_type].append(job)
        request.session["jobs"] = jobs_data
        request.session.modified = True

        return redirect("saisie_jobs", class_type=class_type)

    # Passer les données au template
    class_jobs = jobs_data.get(class_type, [])
    return render(request, "page/page/saisie_jobs.html", {
        "class_type": class_type,
        "class_jobs": class_jobs,
        "session_data": request.session
    })


def johnson(c):
 u=[]
 v=[]
 n=len(c)
 for i in range(n):
     if c[i]["machine_times"][0]>=c[i]["machine_times"][1]:
         v.append(c[i])
     else:
         u.append(c[i])

 v= sorted(v, key=lambda job: job["machine_times"][1], reverse=True)
 u= sorted(u, key=lambda job: job["machine_times"][0])
 s=u+v
 return s


from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import base64


def johnson2(jobs_details):
    sequence_optimal = []

    for job in jobs_details:
        print(f"Traitement du job: {job['job_id']}")
        print(f"Temps de machine: {job['machine_times']}")

        # Vérification des temps de préparation
        if isinstance(job['machine_times'][0], dict) and isinstance(job['machine_times'][1], dict):
            try:
                preparation_time_machine_1 = int(job['machine_times'][0]['preparation_time'])
                preparation_time_machine_2 = int(job['machine_times'][1]['preparation_time'])
            except ValueError:
                raise ValueError(f"Les temps de machine pour le job {job['job_id']} doivent être des nombres.")
        else:
            raise ValueError(
                f"Les temps de machine pour le job {job['job_id']} doivent être des dictionnaires valides.")

        # Traitement logique du job (exemple de calcul)
        c = [[0, 0], [0, 0]]  # Initialisation de la structure pour les temps
        c[0][0] = preparation_time_machine_1
        c[1][0] = preparation_time_machine_2

        print(f"Temps calculés: {c}")

    return sequence_optimal


def vue_johnson(request):
    # Récupérer les jobs depuis la session
    jobs_details = request.session.get('jobs_details', [])
    num_machines = request.session.get('num_machines', 0)

    # Vérification de la condition de l'algorithme de Johnson : 2 machines
    if num_machines != 2:
        raise ValueError("L'algorithme de Johnson ne fonctionne que pour 2 machines.")

    # Appliquer l'algorithme de Johnson pour obtenir la séquence optimale
    sequence_optimal = johnson2(jobs_details)

    # Initialisation des matrices pour le calcul des temps de début et de fin
    num_jobs = len(sequence_optimal)
    s = [[0] * num_jobs for _ in range(num_machines)]
    c = [[0] * num_jobs for _ in range(num_machines)]

    # Calcul des temps de début et de fin pour chaque job sur chaque machine
    s[0][0] = int(sequence_optimal[0]['arrival_date'])
    c[0][0] = s[0][0] + int(sequence_optimal[0]['machine_times'][0])

    for i in range(1, num_jobs):
        prep_time = int(sequence_optimal[i]['machine_times'][0])
        s[0][i] = max(int(sequence_optimal[i]['arrival_date']), c[0][i - 1])
        c[0][i] = s[0][i] + prep_time

    for i in range(1, num_machines):
        prep_time = int(sequence_optimal[0]['machine_times'][i])
        s[i][0] = max(c[i - 1][0], int(sequence_optimal[0]['arrival_date']))
        c[i][0] = s[i][0] + prep_time

        for j in range(1, num_jobs):
            prep_time = int(sequence_optimal[j]['machine_times'][i])
            s[i][j] = max(c[i - 1][j], c[i][j - 1])
            c[i][j] = s[i][j] + prep_time

    # Calcul des métriques : retard et temps de passage
    tardiness = [max(0, c[num_machines - 1][i] - int(sequence_optimal[i].get('delivery_date', 0))) for i in
                 range(num_jobs)]
    flow_times = [c[num_machines - 1][i] - int(sequence_optimal[i].get('arrival_date', 0)) for i in range(num_jobs)]

    total_tardiness = sum(tardiness)
    max_tardiness = max(tardiness) if tardiness else 0
    total_flow_time = sum(flow_times)

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))
    job_colors = {job['job_id']: f"C{idx}" for idx, job in enumerate(sequence_optimal)}

    for i in range(num_machines):
        for j in range(num_jobs):
            start = s[i][j]
            end = c[i][j]
            job_id = sequence_optimal[j]['job_id']
            ax.barh(f"Machine {i + 1}", end - start, left=start, color=job_colors[job_id], edgecolor="black")

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Algorithme de Johnson")
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    handles, labels = ax.get_legend_handles_labels()
    unique_labels = sorted(set(zip(labels, handles)), key=lambda x: int(x[0]))
    ax.legend([handle for label, handle in unique_labels], [label for label, handle in unique_labels],
              loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=num_jobs)

    # Enregistrer le graphique en base64
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png).decode('utf-8')

    # Combiner les données pour les afficher dans la page
    combined_data = [
        {
            "job_id": job['job_id'],
            "arrival_date": job.get('arrival_date', 0),
            "delivery_date": job.get('delivery_date', 0),
            "flow_time": flow_times[i],
            "retard": tardiness[i],
        }
        for i, job in enumerate(sequence_optimal)
    ]

    # Rendu final
    return render(request, 'page/fifo_sanscontrainte.html', {
        'graph': graph,
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'combined_data': combined_data,
        'total_flow_time': total_flow_time,
        'total_retard': total_tardiness,
        'max_retard': max_tardiness,
        'cmax': c[num_machines - 1][num_jobs - 1]
    })


from django.shortcuts import render

from django.shortcuts import render
import json
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
def ordjobshop2gantt(request):
    import matplotlib.pyplot as plt
    import io
    import base64

    # Récupération des données de la session
    session = request.session
    jobs_C12 = session.get('jobs_C12', [])
    jobs_C1 = session.get('jobs_C1', [])
    jobs_C21 = session.get('jobs_C21', [])
    jobs_C2 = session.get('jobs_C2', [])

    # Application de la règle de Johnson pour organiser les jobs C12 et C21
    jobs_C12 = johnson(jobs_C12)  # Tri des jobs pour C12
    jobs_C21 = johnson(jobs_C21)  # Tri des jobs pour C21

    # Mise à jour des jobs triés dans la session
    session['jobs_C12'] = jobs_C12
    session['jobs_C21'] = jobs_C21

    # Concatenation des séquences pour M1 et M2
    M1 = jobs_C12 + jobs_C1 + jobs_C21
    M2 = jobs_C21 + jobs_C2 + jobs_C12

    # Initialisation des listes pour les temps de début et de fin
    S1, C1, S2, C2 = [0] * len(M1), [0] * len(M1), [0] * len(M2), [0] * len(M2)
    C1ind, C2ind = [0] * len(M1), [0] * len(M2)

    # Calcul des temps pour Machine 1
    if M1:
        C1[0] = M1[0]["machine_times"][0]
        C1ind[0] = M1[0]['job_id']
        for i in range(1, len(M1)):
            S1[i] = C1[i - 1]
            C1[i] = S1[i] + M1[i]["machine_times"][0]
            C1ind[i] = M1[i]['job_id']

    # Calcul des temps pour Machine 2
    if M2:
        C2[0] = M2[0]["machine_times"][1]
        C2ind[0] = M2[0]['job_id']
        for i in range(1, len(M2)):
            S2[i] = C2[i - 1]
            C2[i] = S2[i] + M2[i]["machine_times"][1]
            C2ind[i] = M2[i]['job_id']

    # Résolution des conflits entre Machine 1 et Machine 2
    for i in range(len(C1ind)):
        if C1ind[i] in C2ind:
            ind = C2ind.index(C1ind[i])  # Trouver l'indice correspondant dans M2
            if S1[i] > S2[ind] and S1[i] < C2[ind]:
                v = C2[ind] - S1[i]
                for d in range(i, len(C1)):
                    C1[d] += v
                    S1[d] += v
            if S2[ind] > S1[i] and S2[ind] < C1[i]:
                v = C1[i] - S2[ind]
                for d in range(ind, len(C2)):
                    C2[d] += v
                    S2[d] += v

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(14, 6))

    # Tracer les jobs pour Machine 1
    for i, job in enumerate(M1):
        ax.barh(1, C1[i] - S1[i], left=S1[i], color='blue', edgecolor='black', label='Machine 1' if i == 0 else "")
        ax.text(S1[i] + (C1[i] - S1[i]) / 2, 1, f"Job {job['job_id']}", va='center', ha='center', color='white', fontsize=8)

    # Tracer les jobs pour Machine 2
    for i, job in enumerate(M2):
        ax.barh(0, C2[i] - S2[i], left=S2[i], color='orange', edgecolor='black', label='Machine 2' if i == 0 else "")
        ax.text(S2[i] + (C2[i] - S2[i]) / 2, 0, f"Job {job['job_id']}", va='center', ha='center', color='white', fontsize=8)

    # Mise en forme
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Machine 2', 'Machine 1'])
    ax.set_xlabel('Temps', fontsize=12)
    ax.set_title('Diagramme de Gantt pour l\'atelier Job Shop', fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Ajustement des limites
    ax.set_xlim(0, max(max(C1), max(C2)) + 5)  # Ajouter une marge pour la lisibilité

    # Sauvegarde en mémoire pour Base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Passer l'image Gantt à la template
    return render(request, 'page/gantt_chart.html', {
        'gantt_image': image_data
    })


from django.shortcuts import render
from django.http import JsonResponse




from django.shortcuts import render, redirect

def probleme2(request):
    if request.method == "POST":
        # Récupération des données du formulaire
        num_jobs = int(request.POST.get('num_jobs'))
        num_machines = int(request.POST.get('num_machines'))

        # Stockage des données dans la session
        request.session['num_jobs'] = num_jobs
        request.session['num_machines'] = num_machines

        # Redirection vers la page suivante
        return redirect('jobs_detail2')  # Par exemple, vers un formulaire pour saisir les détails des jobs et machines

    return render(request, 'page/probleme.html')
from django.shortcuts import render, redirect

def jobs_detail2(request):
        if request.method == "POST":
            # Récupération des données de session
            num_jobs = request.session.get('num_jobs', 1)
            num_machines = request.session.get('num_machines', 1)

            # Initialisation de la structure des jobs
            jobs_data = {}

            # Collecte des données du formulaire
            for job in range(1, num_jobs + 1):
                ordre_machine = []
                temps_traitement = []

                for operation in range(1, num_machines + 1):
                    # Récupérer la machine et le temps de traitement pour chaque opération
                    machine = int(request.POST.get(f'machine_{job}_{operation}'))
                    temps = int(request.POST.get(f'temps_{job}_{operation}'))

                    # Ajout des données dans les listes
                    ordre_machine.append(machine)
                    temps_traitement.append(temps)

                # Stocker les données de chaque job dans le dictionnaire
                jobs_data[f'j{job}'] = {
                    'ordre_machine': ordre_machine,
                    'temps_traitement': temps_traitement,
                }

            # Stocker les données dans la session
            request.session['jobs_data'] = jobs_data

            # Rediriger vers une page de confirmation
            return redirect('contraintjobshop')
            # Remplace par la vue de confirmation appropriée


                # Génération des données pour le formulaire
        num_jobs = request.session.get('num_jobs', 1)
        num_machines = request.session.get('num_machines', 1)
        jobs_range = range(1, num_jobs + 1)
        machines_range = range(1, num_machines + 1)

        return render(request, 'page/jobs_detail2.html', {
            'jobs_range': jobs_range,
            'machines_range': machines_range,
        })






from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import urllib, base64

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render

def gantt_jobshop(request):
    # Récupération des données de session
    jobs_data = request.session.get('jobs_data', {})


    # Conversion sécurisée en entiers
    for job, data in jobs_data.items():
        data['ordre_machine'] = [int(i) for i in data['ordre_machine']]
        data['temps_traitement'] = [int(i) for i in data['temps_traitement']]

    # Initialisation des disponibilités
    Disponibilite_Mi = {i: 0 for i in range(1, 4)}
    Disponibilite_job = {job: 0 for job in jobs_data.keys()}
    Cmax = 0

    gantt_data = []

    # Ordonnancement des jobs SOP par tri croissant
    for o in range(1, 4):
        # Trier les jobs par date de fin croissante à l'ordre précédent
        jobs_trie = sorted(jobs_data.keys(), key=lambda j: Disponibilite_job[j])

        for job in jobs_trie:
            data = jobs_data[job]
            ordre_machine = data['ordre_machine']
            temps_traitement = data['temps_traitement']

            if o <= len(ordre_machine):
                machine = ordre_machine[o-1]
                temps = temps_traitement[o-1]

                # Calcul de la disponibilité croisée
                date_debut = max(Disponibilite_Mi[machine], Disponibilite_job[job])
                date_fin = date_debut + temps

                # Mise à jour des disponibilités
                Disponibilite_Mi[machine] = date_fin
                Disponibilite_job[job] = date_fin

                # Stockage des données pour le diagramme de Gantt
                gantt_data.append((job, machine, date_debut, date_fin))

                # Mise à jour du Cmax
                Cmax = max(Cmax, Disponibilite_job[job])

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Palette de couleurs diversifiées
    diverse_colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

    # Générer le diagramme avec des couleurs spécifiques
    for idx, (job, machine, start, end) in enumerate(gantt_data):
        color_idx = hash(job) % len(diverse_colors)
        ax.barh(f"Machine {machine}", end - start, left=start, color=diverse_colors[color_idx], edgecolor='black')
        ax.text(start + (end - start) / 2, f"Machine {machine}", f"{job} ({start}-{end})",
                ha='center', va='center', color='black', fontsize=8)

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Ordonnancement des jobs SOP")
    plt.grid(True, linestyle='--', alpha=0.6)

    # Sauvegarder l'image dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Rendre le template
    return render(request, 'page/gantt_jobshop.html', {'image_base64': image_base64, 'Cmax': Cmax})


def gantt_jobshopSPT(request):

        # Récupération des données de session
        jobs_data = request.session.get('jobs_data', {})

        # Trier les jobs selon la règle SPT (Shortest Processing Time)
        jobs_data = dict(sorted(jobs_data.items(), key=lambda item: sum(item[1]['temps_traitement'])))

        # Conversion sécurisée en entiers
        for job, data in jobs_data.items():
            data['ordre_machine'] = [int(i) for i in data['ordre_machine']]
            data['temps_traitement'] = [int(i) for i in data['temps_traitement']]

        # Initialisation des disponibilités
        Disponibilite_Mi = {i: 0 for i in range(1, 4)}
        Disponibilite_job = {job: 0 for job in jobs_data.keys()}
        Cmax = 0

        gantt_data = []

        # Ordonnancement des jobs selon SPT
        for o in range(1, 4):
            # Trier les jobs par date de fin croissante à l'ordre précédent
            jobs_trie = sorted(jobs_data.keys(), key=lambda j: Disponibilite_job[j])

            for job in jobs_trie:
                data = jobs_data[job]
                ordre_machine = data['ordre_machine']
                temps_traitement = data['temps_traitement']

                if o <= len(ordre_machine):
                    machine = ordre_machine[o - 1]
                    temps = temps_traitement[o - 1]

                    # Calcul de la disponibilité croisée
                    date_debut = max(Disponibilite_Mi[machine], Disponibilite_job[job])
                    date_fin = date_debut + temps

                    # Mise à jour des disponibilités
                    Disponibilite_Mi[machine] = date_fin
                    Disponibilite_job[job] = date_fin

                    # Stockage des données pour le diagramme de Gantt
                    gantt_data.append((job, machine, date_debut, date_fin))

                    # Mise à jour du Cmax
                    Cmax = max(Cmax, Disponibilite_job[job])

        # Création du diagramme de Gantt
        fig, ax = plt.subplots(figsize=(10, 6))

        # Palette de couleurs diversifiées
        diverse_colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

        # Générer le diagramme avec des couleurs spécifiques
        for idx, (job, machine, start, end) in enumerate(gantt_data):
            color_idx = hash(job) % len(diverse_colors)
            ax.barh(f"Machine {machine}", end - start, left=start, color=diverse_colors[color_idx], edgecolor='black')
            ax.text(start + (end - start) / 2, f"Machine {machine}", f"{job} ({start}-{end})",
                    ha='center', va='center', color='black', fontsize=8)

        ax.set_xlabel("Temps")
        ax.set_ylabel("Machines")
        ax.set_title("Diagramme de Gantt - Ordonnancement des jobs SPT")
        plt.grid(True, linestyle='--', alpha=0.6)

        # Sauvegarder l'image dans un buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Rendre le template
        return render(request, 'page/gantt_jobshop.html', {'image_base64': image_base64, 'Cmax': Cmax})


def gantt_jobshopLPT(request):
    # Récupération des données de session
    jobs_data = request.session.get('jobs_data', {})

    # Trier les jobs selon la règle SPT (Shortest Processing Time)

    sorted_jobs_data_desc = dict(
        sorted(jobs_data.items(), key=lambda item: sum(item[1]['temps_traitement']), reverse=True))
    # Conversion sécurisée en entiers
    for job, data in jobs_data.items():
        data['ordre_machine'] = [int(i) for i in data['ordre_machine']]
        data['temps_traitement'] = [int(i) for i in data['temps_traitement']]

    # Initialisation des disponibilités
    Disponibilite_Mi = {i: 0 for i in range(1, 4)}
    Disponibilite_job = {job: 0 for job in jobs_data.keys()}
    Cmax = 0

    gantt_data = []

    # Ordonnancement des jobs selon SPT
    for o in range(1, 4):
        # Trier les jobs par date de fin croissante à l'ordre précédent
        jobs_trie = sorted(jobs_data.keys(), key=lambda j: Disponibilite_job[j])

        for job in jobs_trie:
            data = jobs_data[job]
            ordre_machine = data['ordre_machine']
            temps_traitement = data['temps_traitement']

            if o <= len(ordre_machine):
                machine = ordre_machine[o - 1]
                temps = temps_traitement[o - 1]

                # Calcul de la disponibilité croisée
                date_debut = max(Disponibilite_Mi[machine], Disponibilite_job[job])
                date_fin = date_debut + temps

                # Mise à jour des disponibilités
                Disponibilite_Mi[machine] = date_fin
                Disponibilite_job[job] = date_fin

                # Stockage des données pour le diagramme de Gantt
                gantt_data.append((job, machine, date_debut, date_fin))

                # Mise à jour du Cmax
                Cmax = max(Cmax, Disponibilite_job[job])

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))

    # Palette de couleurs diversifiées
    diverse_colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

    # Générer le diagramme avec des couleurs spécifiques
    for idx, (job, machine, start, end) in enumerate(gantt_data):
        color_idx = hash(job) % len(diverse_colors)
        ax.barh(f"Machine {machine}", end - start, left=start, color=diverse_colors[color_idx], edgecolor='black')
        ax.text(start + (end - start) / 2, f"Machine {machine}", f"{job} ({start}-{end})",
                ha='center', va='center', color='black', fontsize=8)

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Ordonnancement des jobs LPT")
    plt.grid(True, linestyle='--', alpha=0.6)

    # Sauvegarder l'image dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Rendre le template
    return render(request, 'page/gantt_jobshop.html', {'image_base64': image_base64, 'Cmax': Cmax})



def contraintjobshop(request):
    if request.method == "POST":
        # Récupérer la contrainte sélectionnée
        selected_contraint = request.POST.get('contraint')

        # Enregistrer dans la session
        request.session['contrainte'] = selected_contraint

        # Redirection vers une autre page (ou confirmation)
        if  request.session['contrainte'] == " Avec preparation":
           return redirect('setup_time_view')  # Exemple : redirection vers une autre vue

        else:

            if request.session['regle'] == "LPT":
            # Rediriger vers une page de confirmation
                 return redirect('setup_time_gantt')
            # Remplace par la vue de confirmation appropriée
            else:
                return redirect('gantt_jobshopSPT')

    return render(request, 'page/contraintjobshop.html')





# page/views.py
from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
import io
import base64

# page/views.py
from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
import io
import base64

# page/views.py
from django.shortcuts import render, redirect
import matplotlib.pyplot as plt
import io
import base64

from django.shortcuts import render, redirect

from django.shortcuts import render, redirect

import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect


def setup_time_view(request):
    if request.method == 'POST':
        # Récupération des données de la session ou initialisation par défaut
        num_machines = int(request.session.get('num_machines', 3))
        num_jobs = int(request.session.get('num_jobs', 3))
        jobs_list = [f"j{i + 1}" for i in range(num_jobs)]  # Liste des jobs

        setup_time = {}
        for m in range(1, num_machines + 1):
            setup_time[m] = {}
            for job_courant in jobs_list:
                setup_time[m][job_courant] = {}
                for job_precedent in jobs_list:
                    field_name = f"setup_time_{m}_{job_courant}_{job_precedent}"
                    try:
                        value = int(request.POST.get(field_name, '0'))  # Conversion sécurisée
                    except ValueError:
                        value = 0  # Valeur par défaut en cas d'erreur
                    setup_time[m][job_courant][job_precedent] = value

        # Enregistrer les données dans la session
        request.session['setup_time'] = setup_time
          # Redirection après enregistrement
        if request.session['regle'] == "LPT":
            # Rediriger vers une page de confirmation
            return redirect('setup_time_ganttLPT')
        # Remplace par la vue de confirmation appropriée
        else:
            return redirect('setup_time_gantt')
    else:
        # Initialisation des variables pour le formulaire
        machines_range = range(1, int(request.session.get('num_machines', 3)) + 1)
        jobs_list = [f"j{i + 1}" for i in range(int(request.session.get('num_jobs', 3)))]
        context = {'machines_range': machines_range, 'jobs_list': jobs_list}
        return render(request, 'page/setup_time_form.html', context)


def display_setup_time_view(request):
    # Récupération des données depuis la session
    setup_time = request.session.get('setup_time', None)

    if not setup_time or not isinstance(setup_time, dict):
        # Message d'erreur si aucune donnée n'est disponible
        context = {
            'error': "Aucun temps de réglage enregistré. Veuillez les configurer d'abord."
        }
        return render(request, 'page/display_setup_time.html', context)

    # Préparer les données pour l'affichage
    num_machines = len(setup_time)
    jobs_list = list(next(iter(setup_time.values())).keys())  # Récupérer les jobs à partir de la première machine

    context = {
        'setup_time': setup_time,
        'num_machines': num_machines,
        'jobs_list': jobs_list,
    }
    return render(request, 'page/c.html', context)

import matplotlib
matplotlib.use('Agg')

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render
import matplotlib

matplotlib.use('Agg')  # Utilisation du backend non interactif

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib

matplotlib.use('Agg')  # Utilisation du backend non interactif

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib

matplotlib.use('Agg')  # Utilisation du backend non interactif

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib

matplotlib.use('Agg')  # Utilisation du backend non interactif

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render

import matplotlib

matplotlib.use('Agg')  # Utilisation du backend non interactif

from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render



import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render

def setup_time_gantt(request):
    # Récupération des données
    setup_time = {int(k): {str(j): {str(i): int(v) for i, v in d.items()} for j, d in v.items()} for k, v in
                  request.session.get('setup_time', {}).items()}
    jobs_data = {str(k): {str(i): v if not isinstance(v, list) else [int(x) for x in v] for i, v in d.items()} for k, d
                 in request.session.get('jobs_data', {}).items()}

    if not setup_time or not jobs_data:
        return render(request, 'page/gantt_jobshopprep.html', {
            'error': "Données manquantes. Veuillez configurer les temps de réglage et les jobs."
        })

    # Initialisation
    num_machines = len(setup_time)
    Disponibilite_Mi = {i: 0 for i in range(1, num_machines + 1)}
    Dernier_job_Mi = {i: None for i in range(1, num_machines + 1)}
    Disponibilite_job = {job: 0 for job in jobs_data.keys()}

    gantt_data = []
    preparation_data = []

    # Ordonnancement
    for o in range(max(len(data['ordre_machine']) for data in jobs_data.values())):
        for job, data in sorted(jobs_data.items(), key=lambda x: sum(x[1]['temps_traitement'])):
            if o < len(data['ordre_machine']):
                machine = data['ordre_machine'][o]
                temps = int(data['temps_traitement'][o])
                job_precedent = Dernier_job_Mi[machine] or job

                # Récupération sécurisée du temps de réglage
                temps_preparation = setup_time[machine].get(job_precedent, {}).get(job, 0)

                # Calcul des dates
                date_debut_preparation = Disponibilite_Mi[machine]
                date_debut_traitement = max(date_debut_preparation + temps_preparation, Disponibilite_job[job])
                date_fin = date_debut_traitement + temps

                # Mise à jour des disponibilités
                Disponibilite_Mi[machine] = date_fin
                Disponibilite_job[job] = date_fin
                Dernier_job_Mi[machine] = job

                # Stockage des données pour le diagramme
                if temps_preparation > 0:
                    preparation_data.append(
                        (machine, date_debut_preparation, date_debut_preparation + temps_preparation))
                gantt_data.append((job, machine, date_debut_traitement, date_fin))

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))
    couleurs = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

    for machine, start, end in preparation_data:
        ax.barh(f"Machine {machine}", end - start, left=start, color='none', hatch='//', edgecolor='black')

    for job, machine, start, end in gantt_data:
        color_idx = hash(job) % len(couleurs)
        ax.barh(f"Machine {machine}", end - start, left=start, color=couleurs[color_idx], edgecolor='black')
        ax.text(start + (end - start) / 2, f"Machine {machine}", f"{job} ({start}-{end})",
                ha='center', va='center', color='black', fontsize=8)

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Ordonnancement avec Préparation")
    plt.grid(True, linestyle='--', alpha=0.6)

    # Sauvegarde de l'image
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'page/gantt_jobshopprep.html', {'graphic': graph})



import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render

def setup_time_ganttLPT(request):
    # Récupération des données
    setup_time = {int(k): {str(j): {str(i): int(v) for i, v in d.items()} for j, d in v.items()} for k, v in
                  request.session.get('setup_time', {}).items()}
    jobs_data = {str(k): {str(i): v if not isinstance(v, list) else [int(x) for x in v] for i, v in d.items()} for k, d
                 in request.session.get('jobs_data', {}).items()}

    if not setup_time or not jobs_data:
        return render(request, 'page/gantt_jobshopprep.html', {
            'error': "Données manquantes. Veuillez configurer les temps de réglage et les jobs."
        })

    # Initialisation
    num_machines = len(setup_time)
    Disponibilite_Mi = {i: 0 for i in range(1, num_machines + 1)}
    Dernier_job_Mi = {i: None for i in range(1, num_machines + 1)}
    Disponibilite_job = {job: 0 for job in jobs_data.keys()}

    gantt_data = []
    preparation_data = []

    # Ordonnancement
    for o in range(max(len(data['ordre_machine']) for data in jobs_data.values())):
        for job, data in sorted(jobs_data.items(), key=lambda x: sum(x[1]['temps_traitement']), reverse=True):
            if o < len(data['ordre_machine']):
                machine = data['ordre_machine'][o]
                temps = int(data['temps_traitement'][o])
                job_precedent = Dernier_job_Mi[machine] or job

                # Récupération sécurisée du temps de réglage
                temps_preparation = setup_time[machine].get(job_precedent, {}).get(job, 0)

                # Calcul des dates
                date_debut_preparation = Disponibilite_Mi[machine]
                date_debut_traitement = max(date_debut_preparation + temps_preparation, Disponibilite_job[job])
                date_fin = date_debut_traitement + temps

                # Mise à jour des disponibilités
                Disponibilite_Mi[machine] = date_fin
                Disponibilite_job[job] = date_fin
                Dernier_job_Mi[machine] = job

                # Stockage des données pour le diagramme
                if temps_preparation > 0:
                    preparation_data.append(
                        (machine, date_debut_preparation, date_debut_preparation + temps_preparation))
                gantt_data.append((job, machine, date_debut_traitement, date_fin))

    # Création du diagramme de Gantt
    fig, ax = plt.subplots(figsize=(10, 6))
    couleurs = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

    for machine, start, end in preparation_data:
        ax.barh(f"Machine {machine}", end - start, left=start, color='none', hatch='//', edgecolor='black')

    for job, machine, start, end in gantt_data:
        color_idx = hash(job) % len(couleurs)
        ax.barh(f"Machine {machine}", end - start, left=start, color=couleurs[color_idx], edgecolor='black')
        ax.text(start + (end - start) / 2, f"Machine {machine}", f"{job} ({start}-{end})",
                ha='center', va='center', color='black', fontsize=8)

    ax.set_xlabel("Temps")
    ax.set_ylabel("Machines")
    ax.set_title("Diagramme de Gantt - Ordonnancement avec Préparation")
    plt.grid(True, linestyle='--', alpha=0.6)

    # Sauvegarde de l'image
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'page/gantt_jobshopprep.html', {'graphic': graph})



from django.shortcuts import render, redirect

from django.shortcuts import render, redirect

def regleopt(request):

    return render(request, 'page/optimisation.html')
