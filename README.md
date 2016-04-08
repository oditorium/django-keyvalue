# django-keyvalue
_a hierarchical key-value storage module for Django_

## Installation

You must have Python 3 and Django installed (developed on Python 3.5 and Django 1.9, but earlier 
versions should work as well)


### Installing the `keyvalue` app

The keyvalue app can be copied into any Django project. Don't forget to add it to `settings.py`

	INSTALLED_APPS += [
	    'keyvalue',
	]

and then to run the migrations

	python3 manage.py makemigrations
	python3 manage.py migrate

You should also run the unit tests

	python3 manage.py test


### Installing `keyvalue.py` into another app

The main content of this library is contained in the module `keyvalue.py` that should plug right into
any Django project. Note that `keyvalue.py` is a models module, so if it is not installed in its
own app it must be added to another one. The most elegant way to do that is to use a models _package_
instead of a models _module_ (see also the `keyvalue` app which employs the same structure):

1. create a `models` directory within the app directory (in the same place where one finds the regular
`models.py` module)

2. move `models.py` into the `models` directory

3. copy `keyvalue.py` into the `models` directory

4. create a file `__init__.py` in the `models` directory

The file `__init__.py` should contain the following lines

	from .models import *
	from .keyvalue import *

Once this is done you need to migrate the database using

	python3 manage.py makemigrations
	python3 manage.py migrate

You should also copy the unit test file `tests_keyvalue.py` into that app directory.
The test are then run as usual using

	python3 manage.py test

### Heroku installation

The following commands should install this entire repo on Heroku: after installing the Heroku [Toolbelt](https://toolbelt.heroku.com/) run

	git clone https://github.com/oditorium/django-keyvalue.git
	cd django-keyvalue
	heroku create
	heroku config:set HEROKU=1
	git push heroku +master

## Using the `keyvalue` library 


### Overview

In order to use the library, the keyvalue models must be imported as usually, eg by doing

	from keyvalue.models import *

assuming the app was installed. This places the following classes into the module's namespace

- `KeyValueStoreBase` - the abstract base class, defining the interface of the key value storage
(which incidentally is mostly a `dict` interface, plus the namespace stuff)

- `KeyValueStoreNull` - a trivial key value storage that does not--and can not--contain any key
value pairs (it is the root storage of all storage hierarchies; there is no need to invoke it
directly)

- `KeyValueStore` - that's the workhorse model class that actually implements the key value storage
using the standard Django SQL adapters (see also the section on additional backends below)

- `KeyValuePair` - that's the model class for the actual key value pairs; there is not usually a 
reason to use this class directly

Note that in most applications the `KeyValueStore` class will be sufficient, so the parsimonious
way of using this library is

	from keyvalue.models import KeyValueStore

### Using a non-hierarchical storage

By default, the storage is namespaced, and key value pairs in different namespaces do not interfere.
To use a storage (and create one, if it does not exist) use

	kvs = KeyValueStorage.kvs_get("mynamespace")

The storage instance `kvs` then essentially implements a `dict` interface (with the restriction that
currently both keys and values must be strings). The code below should be self explanatory:

	kvs.clear()
	print (len(kvs))				# 0
	kvs["1"] = "1"
	print (len(kvs))				# 1
	print (kvs["1"]) 				# "1"
	print ("1" in kvs)				# True
	kvs["2"] 						# raises KeyError
	kvs.get("2", "-na-") 			# "-na-"
	print ("2" in kvs)				# False
	del kvs["1"]
	print (kvs["1"]) 				# raises KeyError
	print (len(kvs))				# 0
	
It also supports all the usual iterator methods (`keys()`, `values()`, `items()`) as well as direct 
iteration `for k in kvs`. Finally it has an `as_dict` property that allows to extract the current
status of that storage segment into a dict.

On the segment level (segment being a different work for a namespace) it implements the following 
methods (see their respective doc strings for details)

- `kvs_get` - gets a storage segment (can create it if it does not exist)
- `kvs_update` - initialises a storage segment
- `kvs_delete` - deletes a storage segment
- `kvs_exists` - checks whether a storage segment exists

### Using a hierarchical storage

When hierarchical storage is used, namespaces are essentially considered trees. A hierarchical storage is
created using the following command

	kvs = KeyValueStorage.kvs_get("aaa::bbb", "::")

Hierarchical storage is used if and only if a hierarchy separator is given (here "::", but any other 
non-empty string can be used). The above command actually gets (or creates) two namespaces, `aaa` and
`aaa::bbb`, and the parent namespace can be accessed using the `parent` method

	print (kvs.namespace) 				# 'aaa::bbb'
	print (kvs.parent.namespace) 		# 'aaa'

The height of a namespace is returned using the `height` property

	print (kvs.height) 						# 2
	print (kvs.parent.height) 				# 1
	print (kvs.parent.parent.height) 		# 0

Note that the namespace at height 0 is always a `KeyValueStorageNull` segment

	print ( isinstance(kvs.parent.parent, KeyValueStorageNull) ) 		# True

As one would expect, if another namespace is created with the command

	kvs2 = KeyValueStorage.kvs_get("aaa::ccc", "::")

then `kvs` and `kvs2` are distinct namespaces, but their parent is the same `aaa` namespace.

Hierarchical namespaces are merged, with higher up-definitions hiding those below. For example

	kvs_b = KeyValueStorage.kvs_get("aaa::bbb", True)
		# equivalent: kvs_b = KeyValueStorage.kvs_get(["aaa", "bbb"])
	kvs_c = KeyValueStorage.kvs_get("aaa::ccc", True)
	kvs_a = kvs_b.parent

	kvs_a["1"] = "a1"
	print ( kvs_a("1") )		# "a1"
	print ( kvs_b("1") )		# "a1"
	print ( kvs_c("1") )		# "a1"

	kvs_b["1"] = "b1"
	kvs_b["1"] = "c1"
	print ( kvs_a("1") )		# "a1"
	print ( kvs_b("1") )		# "b1"
	print ( kvs_c("1") )		# "c1"
	
	del kvs_b["1"]
	print ( kvs_a("1") )		# "a1"
	print ( kvs_b("1") )		# "a1"
	print ( kvs_c("1") )		# "c1"

The general rule is that all _read_ commands look at the entire hierarchy, whilst all _write_
(and _delete_) commands only look at the particular segment.


## Adding additional backends

The `KeyValueStorage` class only employs five backend methods that link the class' functionality
to the actual storage backend, three of those on the key-value pair level, and two on the segment
level. The methods and properties on the single item level are

-  `_all_items` - gets iterator over all items in this segment
- `_item` - gets one particular item
- `_create_item` - creates a new item

and those on the segment level are

- `_kvs_retrieve` - reads an existing segment object
- `_kvs_create` - creates a new segment object

It is also assumed that all instances implement a `delete()` method that erases them from the storage
backend. 

So if someone is interested say porting this module to Redis, all one have to do its

	class KeyValueStorageRedis(KeyValueStorage)
	
		@property
		def _all_items(self)
			...

(well actually this is not quite right because `KeyValueStorage` also derives from `models.Model` which
would not make sense for Redis, so some intermediate class would need to be established, but this is not
that hard I suppose)

## Contributions
Contributions welcome. Send us a pull request!

## Credits
This code is based on a [snippet](https://djangosnippets.org/snippets/2451/) by Morgul

## Change Log
The idea is to use [semantic versioning](http://semver.org/), even though initially we might make some minor
API changes without bumping the major version number. Be warned!

- **v2.1** allowing the namespace to be a list
- **v2.0** added hierarchical storage (initial published version of the library)
- **v1.0** key value storage with completely independent segments (not hierarchical)
