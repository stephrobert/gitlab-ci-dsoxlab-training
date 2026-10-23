# Scénario

Le pipeline de `pipeline-craft` est **vert**, et il le restera quoi que vous
fassiez de ses secrets. C'est précisément le problème : un secret mal rangé ne
casse rien, il s'expose.

Deux secrets vivent dans les variables CI/CD du projet :

- **`SERVICE_TOKEN`**, un jeton d'accès de projet (`service-v1`) avec lequel le
  job `joindre-le-service` appelle l'API de la forge. La variable n'est ni
  protégée ni masquée ;
- **`DEPLOY_KEY`**, une clé SSH de déploiement sur plusieurs lignes. La variable
  est ordinaire, et le job `installer-la-cle` la recopie à la main dans un
  fichier.

La branche `main` est protégée. Le projet est dans la forge du lab. Une copie du
dépôt vous attend sur la machine, avec une note : `NOTE-SECRETS.txt`.

## Mission

Trois gestes, et le troisième est celui qu'on repousse toujours.

1. **Protéger et masquer le jeton de service.** Une variable protégée n'est
   remise qu'aux pipelines des branches protégées ; une variable masquée est
   remplacée par `[MASKED]` dans les journaux.
2. **Passer la clé de déploiement en variable de type fichier.** Le job ne reçoit
   plus la valeur, il reçoit le **chemin** d'un fichier qui la porte. Il faut donc
   changer le type de la variable **et** adapter le job, sans le casser. La clé
   doit rester protégée.
3. **Renouveler le jeton de service sans interrompre le service.** Le jeton
   `service-v1` est considéré comme compromis. Mettez un **nouveau** jeton en
   service, prouvez par un pipeline qu'il fonctionne, et **seulement alors**
   révoquez l'ancien. Un secret qu'on retire avant d'avoir mis son remplaçant en
   place coupe le service ; un ancien secret qu'on ne révoque jamais reste valable
   pour celui qui l'a copié.

## Ce que le lab vérifie

1. `SERVICE_TOKEN` est **protégée et masquée** dans la forge ;
2. `DEPLOY_KEY` est de **type fichier**, protégée, et sa valeur est intacte ;
3. l'ancien jeton est **révoqué**, la variable porte un **autre jeton valide**, et
   le job `joindre-le-service` n'a **jamais échoué** depuis le départ, tout en
   ayant réussi avec le nouveau jeton ;
4. le dernier pipeline de `main` est **sain**, ses deux jobs réussissent, et le
   journal de `installer-la-cle` affiche `CLE-SOURCE=fichier` : le job a bien reçu
   la clé sous forme de fichier. Cette ligne est écrite par le job de départ :
   conservez-la en adaptant le job.

Les deux jobs gardent leur nom. Le lab lit les réglages que la forge porte et ce
que ses jobs ont fait, jamais le contenu de `.gitlab-ci.yml`.

Le fait qu'un secret ne doit pas apparaître dans un journal est l'objet du lab
`gl-05-sortir-les-secrets` : ici, le runner masque de lui-même les jetons
`glpat-` et ce sujet ne se joue pas.

## Une limite à connaître

La forge ne date pas la révocation d'un jeton : le lab ne peut pas prouver que
votre nouveau jeton servait **avant** que vous ne révoquiez l'ancien. Il vérifie
ce qui se mesure, et c'est à vous de tenir l'ordre. Dans la vraie vie, la même
règle vaut pour tout secret : on installe le nouveau, on vérifie, puis on
révoque.

## Vault

Un gestionnaire de secrets comme Vault sait émettre des secrets à durée de vie
courte et les renouveler seul. Il est **facultatif** ici : ce lab n'en a pas
besoin et ne l'installe pas.
