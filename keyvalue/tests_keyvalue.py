"""
KeyValue - tests key value storage

(c) Stefan LOESCH, oditorium 2016. All Rights Reserved.

Copyright (c) Stefan LOESCH, oditorium 2016. All Rights Reserved.
Licensed under the MIT License <https://opensource.org/licenses/MIT>.
"""

from django.test import TestCase, RequestFactory
#from django.conf import settings
#from django.core.urlresolvers import reverse_lazy, reverse
#from Presmo.tools import ignore_failing_tests, ignore_long_tests

from .models import KeyValueStoreBase, NullKeyValueStore, KeyValueStore, KeyValuePair

#########################################################################################
## NULL KEY VALUE TEST
class NullKeyValueTest(TestCase):
    
    testKeyValueStore = NullKeyValueStore
        # that's the KVS to be tested; by changing this line it is possible to test
        # another KVS provided it also derives from KeyValueStoreBase

    def setUp(s):
        super().setUp()
        s.KVS = s.testKeyValueStore
      
    def test_structure(s):
        """checks structure of the KVS"""
        s.assertTrue(isinstance(s.KVS(), KeyValueStoreBase))
            # make sure the KVS tested implements the KeyValueStoreBase interface
        
    def test_namespace_creation(s):
        """test whether namespaces get created and are unique"""
        
        kvs1 = s.KVS.kvs_get()
       
    def test_basics(s):
        """tests the basic operations on the storage"""
        
        kvs = s.KVS.kvs_get("test_basics")
        s.assertEqual(len(kvs), 0)
        s.assertEqual("1" in kvs, False)
        with s.assertRaises(KeyError): del kvs["1"]
        kvs.clear()


    def test_collective(s):
        """tests the collective operations on the storage"""
        
        kvs = s.KVS.kvs_get("test_collective")
        s.assertEqual(kvs.as_dict, {})
        s.assertEqual(list(kvs.keys()), [])
        s.assertEqual(list(kvs.values()), [])
        s.assertEqual(list(kvs.items()), [])
        kvs.clear()

    def test_iter(s):
        """tests the iteration interface of the storage"""
        
        kvs = s.KVS.kvs_get("test_iter")
        #print (kvs.__iter__)
        s.assertTrue(  hasattr(kvs, '__iter__')  )
        d = {k:kvs[k] for k in kvs.keys()}
        s.assertEqual(d, {})
        d = [v for v in kvs.values()]
        s.assertEqual(d, [])
        d = [v for v in kvs.items()]
        s.assertEqual(d, [])
        d = {k:kvs[k] for k in kvs}
        s.assertEqual(d, {})


#########################################################################################
## KEY VALUE TEST
class KeyValueTest(TestCase):
    
    testKeyValueStore = KeyValueStore
        # that's the KVS to be tested; by changing this line it is possible to test
        # another KVS provided it also derives from KeyValueStoreBase

    def setUp(s):
        super().setUp()
        s.KVS = s.testKeyValueStore
        s.kvs0 = s.KVS.kvs_get()
        s.kvs1 = s.KVS.kvs_get("ns1")
      
    def test_structure(s):
        """checks structure of the KVS and other sundry stuff"""
        s.assertTrue(isinstance(s.KVS(), KeyValueStoreBase))
            # make sure the KVS tested implements the KeyValueStoreBase interface
        s.assertEqual(  s.KVS.parent_namespace("ns1", "::"), None  )
        s.assertEqual(  s.KVS.parent_namespace("ns1::ns2", "::"), "ns1"  )
        s.assertEqual(  s.KVS.parent_namespace("ns1::ns2::ns3", "::"), "ns1::ns2"  )

        
    def test_namespace_creation(s):
        """test whether namespaces get created and are unique"""
        
        kvs1 = s.KVS.kvs_get()
        s.assertTrue(kvs1.id != None)
        kvs1a = s.KVS.kvs_get()
        s.assertEqual(kvs1.id, kvs1a.id)
        kvs1b = s.KVS.kvs_get("")
        s.assertEqual(kvs1.id, kvs1b.id)
        
        kvs2 = s.KVS.kvs_get("another_ns")
        s.assertTrue(kvs2.id != None)
        kvs2a = s.KVS.kvs_get("another_ns")
        s.assertEqual(kvs2.id, kvs2a.id)
 
       
    def test_basics(s):
        """tests the basic operations on the storage"""
        
        kvs = s.KVS.kvs_get("test_basics")
        kvs1 = s.KVS.kvs_get("test_basics_1")
        s.assertEqual(len(kvs), 0)
        
        kvs["1"] = "v1"
        kvs["2"] = "v2"
        s.assertEqual(len(kvs), 2)
        s.assertEqual(kvs["1"], "v1")
        s.assertEqual(kvs["2"], "v2")
        s.assertEqual(len(kvs1), 0)
        
        kvs["2"] = "v2+"
        s.assertEqual(len(kvs), 2)
        s.assertEqual(kvs["2"], "v2+")
        
        s.assertEqual("1" in kvs, True)
        s.assertEqual("2" in kvs, True)
        s.assertEqual("3" in kvs, False)
        
        del kvs["1"]
        s.assertEqual(len(kvs), 1)
        s.assertEqual("1" in kvs, False)
        
        kvs.clear()
        s.assertEqual(len(kvs), 0)
        s.assertEqual("1" in kvs, False)


    def test_collective(s):
        """tests the collective operations on the storage"""
        
        kvs = s.KVS.kvs_get("test_collective")
        kvs["1"] = "v1"
        kvs["2"] = "v2"
        kvs["3"] = "v3"
        s.assertEqual(kvs.as_dict, {"1":"v1", "2":"v2", "3": "v3"})
        s.assertEqual(list(kvs.keys()), ["1", "2", "3"])
        s.assertEqual(list(kvs.values()), ["v1", "v2", "v3"])
        s.assertEqual(list(kvs.items()), [('1', 'v1'), ('2', 'v2'), ('3', 'v3')])

        kvs["3"] = "v2"
        s.assertEqual(kvs.as_dict, {"1":"v1", "2":"v2", "3": "v2"})
        s.assertEqual(list(kvs.keys()), ["1", "2", "3"])
        s.assertEqual(list(kvs.values()), ["v1", "v2", "v2"])
        s.assertEqual(list(kvs.items()), [('1', 'v1'), ('2', 'v2'), ('3', 'v2')])

        kvs["2"] = "v2b"
        s.assertEqual(kvs.as_dict, {"1":"v1", "2":"v2b", "3": "v2"})
        s.assertEqual(list(kvs.keys()), ["1", "2", "3"])
        s.assertEqual(list(kvs.values()), ["v1", "v2b", "v2"])
        s.assertEqual(list(kvs.items()), [('1', 'v1'), ('2', 'v2b'), ('3', 'v2')])
            # keys remain in the order in which they were initially inserted!

        del kvs["1"]
        s.assertEqual(kvs.as_dict, {"2":"v2b", "3": "v2"})
        s.assertEqual(list(kvs.keys()), ["2", "3"])
        s.assertEqual(list(kvs.values()), ["v2b", "v2"])
        s.assertEqual(list(kvs.items()), [('2', 'v2b'), ('3', 'v2')])

        kvs.clear()
        s.assertEqual(len(kvs), 0)
        

    def test_iter(s):
        """tests the iteration interface of the storage"""
        
        kvs = s.KVS.kvs_get("test_iter")
        kvs["1"] = "v1"
        kvs["2"] = "v2"
        kvs["3"] = "v3"

        d = {k:kvs[k] for k in kvs}
        s.assertEqual(d, {"1":"v1", "2":"v2", "3": "v3"})

        d = {k:kvs[k] for k in kvs.keys()}
        s.assertEqual(d, {"1":"v1", "2":"v2", "3": "v3"})
        
        d = [v for v in kvs.values()]
        s.assertEqual(d, ["v1", "v2", "v3"])
        
        d = [v for v in kvs.items()]
        s.assertEqual(d, [('1', 'v1'), ('2', 'v2'), ('3', 'v3')])
    
    
    def test_globals(s):
        """test the global properties and method"""
        
        s.assertEqual( s.KVS.kvs_exists('test_globals'), False )
        s.KVS.kvs_get('test_globals')
        s.assertEqual( s.KVS.kvs_exists('test_globals'), True )
        s.KVS.kvs_delete('test_globals')
        s.assertEqual( s.KVS.kvs_exists('test_globals'), False )

        dct = {"1":"10", "2": "20"}
        s.KVS.kvs_update('ns2', dct)
        s.assertEqual( s.KVS.kvs_exists('ns2'), True )
        ns2 = s.KVS.kvs_get('ns2')
        s.assertEqual( ns2["1"], "10" )
        
        dct2 = {"1":"100", "3": "300"}
        s.KVS.kvs_update('ns2', dct2, s.KVS.CLEAR)
        s.assertEqual( ns2["1"], "100" )
        s.assertEqual( ns2["3"], "300" )
        s.assertEqual( ns2.get("2"), None )
        
        dct3 = {"2":"200", "3": "3000"}
        s.KVS.kvs_update('ns2', dct3, s.KVS.UPDATE)
        s.assertEqual( ns2["1"], "100" )
        s.assertEqual( ns2["2"], "200" )
        s.assertEqual( ns2["3"], "3000" )
        
        s.KVS.kvs_delete('ns2')
        s.assertEqual( s.KVS.kvs_exists('ns2'), False )

    def test_hierarchic(s):
        """test hierarchic namespaces"""
        
        kvs_nh = s.KVS.kvs_get('non::hierarchic::namespace')
        s.assertEqual( kvs_nh._parent,  None)
        s.assertTrue( isinstance (kvs_nh.parent, NullKeyValueStore) )
        
        kvs2 = s.KVS.kvs_get('hierarchic::namespace', True, True)
        s.assertTrue( kvs2._parent != None)
        kvs1 = kvs2.parent
        s.assertEqual( kvs2.namespace,  'hierarchic::namespace')
        s.assertEqual( kvs2.parent.namespace,  'hierarchic')
        s.assertEqual( kvs1.namespace,  'hierarchic')
        s.assertEqual( kvs2.parent.parent.namespace,  '')
        s.assertEqual( kvs2.parent.parent.parent.namespace,  '')
        
        s.assertEqual( kvs2.height,  2)
        s.assertEqual( kvs2.parent.height,  1)
        s.assertEqual( kvs1.height,  1)
        s.assertEqual( kvs2.parent.parent.height,  0)
        s.assertEqual( kvs2.parent.parent.parent.height,  0)
        
        kvs1["in1"] = "in1"
        s.assertEqual( kvs2["in1"],  "in1")
        s.assertEqual( kvs2.get("in1"),  "in1")
        with s.assertRaises(KeyError): del kvs2["in1"]
        s.assertEqual( list(kvs2.keys()),  ["in1"] )
        s.assertEqual( list(kvs1.keys()),  ["in1"] )
        s.assertEqual( list(kvs2.values()),  ["in1"] )
        s.assertEqual( list(kvs1.values()),  ["in1"] )
        s.assertEqual( list(kvs2.items()),  [("in1", "in1")] )
        s.assertEqual( list(kvs1.items()),  [("in1", "in1")] ) 
        s.assertEqual("in1" in kvs2, True)
        s.assertEqual( kvs2.as_dict, {"in1": "in1"})
        kvs2.clear()
        s.assertEqual("in1" in kvs2, True)

        kvs2["in2"] = "in2"
        s.assertEqual( list(kvs2.keys()),  ["in2", "in1"] )
        s.assertEqual( list(kvs1.keys()),  ["in1"] )
        s.assertEqual( list(kvs2.values()),  ["in2", "in1"] )
        s.assertEqual( list(kvs1.values()),  ["in1"] )
        s.assertEqual( list(kvs2.items()),  [("in2", "in2"), ("in1", "in1")] )
        s.assertEqual( list(kvs1.items()),  [("in1", "in1")] ) 
        
        del kvs1["in1"]
        s.assertEqual("in1" in kvs2, False)
		

        
        
        
        
