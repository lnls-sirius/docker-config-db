# Mongo
[Introduction to Mongo](https://docs.mongodb.com/manual/introduction/)
- Document database
- Each document is a record, which is composed of field and value pair (JSON)

## Acessing the database
- Log into Docker container running the mongo server
  - List of active containers: `docker container ls`
  - Get container name
  - Run bash in existing container: `docker container exec -it {CONTAINER_NAME} bash`
  - Inside the container issue `mongo` to access the mongo shell.

- Mongo Shell:
  - Issue `show dbs` to show existing dbs and theirs names.
  - In order to use a secific db issue: `use {DB_NAME}`.
  - Issuing `show collections` will show a list of the collections available for the db currently being used.

- Find a document:
  
  `db.configs.find()`: This command will return all documents in the *configs* collection.
  
  Optionally you may supply a constraint document in order to filter the selected documents.
  
  E.g.: 
  - `db.config.find( {discarded: true} )` will return all documents in which the field *discarded* is *true*.
  - `db.configs.find( {name: /.*beam.*/} )` will return all documents in which the field *name* has the **beam** substring.

  Another useful parameter the *find* method accepts is a projection document of fields.
  
  E.g.: `db.configs.find( {discarded: true}, {name: true} )` will return all documents in which the field *discarded* is *true*. However, the documents returned will contain only **_id** and **name** fields. Note that the **_id** field will always be present, unless you explicitly remove it in the projection document (e.g.: `{_id: false, name: true}`)

- Delete document

    There are two methods available:
    - *deleteOne*
    - *deleteMany*

    `db.configs.deleteMany({})` will delete all documents from the *configs* collection. BE CAREFUL!!

    Just like the *find* method you can supply a constraint document.

    `db.configs.deleteMany( {discarded: True} )` will delete all documents in which the field *discarded* is *true*.

    Be careful! Always check your constraint list issuing a *find* first.
    
    E.g.: If you want to delete all documents that have the *discarded* field set to *true* first run a *find*:
    - `db.configs.find( {discarded: True} )` or
    - `db.configs.find( {discarded: True} ).pretty()` or yet
    - `db.configs.find( {discarded: True} ).count()` which returns the number of documents matched. 

    After you are certain that these are the documents you wish to remove from the database you may proceed to delete.


  For more check mongo documentation: 
  - [Query Documents](https://docs.mongodb.com/manual/tutorial/query-documents/)
  - [Delete Documents](https://docs.mongodb.com/manual/tutorial/remove-documents/)
