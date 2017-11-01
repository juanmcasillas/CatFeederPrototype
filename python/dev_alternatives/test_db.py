
import db
import datetime


def test_events():
    print "load all events"
    event = db.Event()
    events = manager.LoadAllEvents()
    for i in events:
        print i
        
    print "load event 27"
    e27 = manager.LoadEvent(27)
    
    print "update allowed 27"
    e27.allowed = 0
    manager.UpdateEvent(e27)
    e27 = manager.LoadEvent(27)
    print e27
    print "update allowed 27"
    e27.allowed = 1
    manager.UpdateEvent(e27)
    e27 = manager.LoadEvent(27)
    print e27
    
    print "insert 28"
    e28 = db.Event()
    e28.start = db.FormatDate(datetime.datetime.now()) 
    e28.end =   db.FormatDate(datetime.datetime.now() + datetime.timedelta(minutes = 10))
    e28.rule = 1
    e28.petid = 1
    e28.allowed = 0
 
    manager.InsertEvent(e28)

    print "load all events"
    event = db.Event()
    events = manager.LoadAllEvents()
    for i in events:
        print i    
    
    manager.DeleteEvent(e28)
    
    print "load all events"
    event = db.Event()
    events = manager.LoadAllEvents()
    for i in events:
        print i    
    
def test_pets():
    print "load all pets"
    pet = db.Pet()
    pets = manager.LoadAllPets()
    for i in pets:
        print i
        
    print "load pet 3"
    e3 = manager.LoadPet(3)
    print "update photo 3"
    e3.photo = 'tempphoto.jpg'
    manager.UpdatePet(e3)
    

    e3 = manager.LoadPet(3)
    print e3
    print "update photo e3"
    e3.photo = 'firulais.jpg'
    manager.UpdatePet(e3)
    e3 = manager.LoadPet(3)
    print e3
    
    print "insert e4"
    e4 = db.Pet()
    e4.name = 'demo'
    e4.chipid = 'chip'
    e4.photo = 'photo.jpg'
 
    manager.InsertPet(e4)

    print "load all pets"
    pet = db.Pet()
    pets = manager.LoadAllPets()
    for i in pets:
        print i
    
    manager.DeletePet(e4)
    
    print "load all pets"
    pet = db.Pet()
    pets = manager.LoadAllPets()
    for i in pets:
        print i


def test_rules():
    print "load all rules"
    r = db.Rule()
    rs = manager.LoadAllRules()
    for i in rs:
        print i
        
    print "load rule 1"
    r3 = manager.LoadRule(1)
    print "update desc 1"
    r3.description = 'testing desc'
    manager.UpdateRule(r3)
    

    r3 = manager.LoadRule(1)
    print r3
    print "update desc 1"
    r3.description = 'Allow feeding to neko and eli'
    manager.UpdateRule(r3)
    r3 = manager.LoadRule(1)
    print r3
    
    print "insert e4"
    e4 = db.Rule()
    e4.name = 'demo'
    e4.rule = 'XX'
    e4.description = 'TESTING RULE'
 
    manager.InsertRule(e4)

    print "load all rules"
    r = db.Rule()
    rs = manager.LoadAllRules()
    for i in rs:
        print i
    
    manager.DeleteRule(e4)
    
    print "load all rules"
    r = db.Rule()
    rs = manager.LoadAllRules()
    for i in rs:
        print i


def test_weights():
    print "load all weights"
    r = db.Weight()
    rs = manager.LoadAllWeights()
    for i in rs:
        print i
        
    print "load weights 1"
    r3 = manager.LoadWeight(1)
    print "update weights 1"
    r3.weight = 99
    manager.UpdateWeight(r3)
    

    r3 = manager.LoadWeight(1)
    print r3
    print "update weights 1"
    r3.weight = 4.0
    manager.UpdateWeight(r3)
    r3 = manager.LoadWeight(1)
    print r3
    
    print "insert e4"
    e4 = db.Weight()
    e4.petid = 99
    e4.stamp = db.FormatDate(datetime.datetime.now()) 
    e4.weight = 99.9
 
    manager.InsertWeight(e4)

    print "load all weights"
    r = db.Weight()
    rs = manager.LoadAllWeights()
    for i in rs:
        print i
    
    manager.DeleteWeight(e4)
    
    print "load all weights"
    r = db.Rule()
    rs = manager.LoadAllWeights()
    for i in rs:
        print i

if __name__ == "__main__":
    
    manager = db.Manager("catfeeder.db")
 
    print "-" * 80
    test_events()
 
    print "-" * 80
    test_pets()
 
    print "-" * 80
    test_rules()
    
    print "-" * 80
    test_weights()
     
    manager.CloseAndCommit()