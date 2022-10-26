import csv
import random

# Dictionary to store all quoted triples and their corresponding blank nodes
# key: RDF* triple as string, value: Blank node
bn_dict = dict()
s_URI = "<https://w3c.github.io/rdf-star/unstar#subject>"
p_URI = "<https://w3c.github.io/rdf-star/unstar#predicate>"
o_URI = "<https://w3c.github.io/rdf-star/unstar#object>"
s_flag = "unstar.subject"
p_flag = "unstar.predicate"
o_flag = "unstar.object"

class RDF_Star_Triple():
    
    subj = None
    pred = None
    obj  = None
    
    # Constructor for RDF* Triple. 3-tuples are used to denote nested RDF* triples
    def __init__(self, subj, pred, obj): # recursive constructor
        if isinstance(subj, tuple):
            self.subj = RDF_Star_Triple(subj[0], subj[1], subj[2])
        else:
            self.subj = subj
        
        self.pred = pred
        
        if isinstance(obj, tuple):
            self.obj = RDF_Star_Triple(obj[0], obj[1], obj[2])
        else:
            self.obj  = obj
            
    # Set the subject of the RDF* triple
    def setSubject(self, subj):
        if isinstance(subj, tuple):
            self.subj = RDF_Star_Triple(subj[0], subj[1], subj[2])
        else:
            self.subj = subj
            
    # Set the predicate of the RDF* triple
    def setPredicate(self, pred):
        self.pred = pred
            
    # Set the object of the RDF* triple
    def setObject(self, obj):
        if isinstance(obj, tuple):
            self.obj = RDF_Star_Triple(obj[0], obj[1], obj[2])
        else:
            self.obj  = obj
            
    # Replace old entity name with new entity name
    def replaceAll(self, old, new):
        if self.subj == old:
            self.subj = new
        elif isinstance(self.subj, RDF_Star_Triple):
            self.subj.replaceAll(old, new)
            
        if self.obj == old:
            self.obj = new
        elif isinstance(self.obj, RDF_Star_Triple):
            self.obj.replaceAll(old, new)
            
    # Check is an RDF* triple is also an RDF triple
    def isRDFTriple(self):
        return not isinstance(self.subj, RDF_Star_Triple) and not isinstance(self.obj, RDF_Star_Triple)
            
    # Check how many triples deep is the RDF* triple
    def level(self): 
        if not isinstance(self.subj, RDF_Star_Triple) and not isinstance(self.obj, RDF_Star_Triple):
            return 0
        elif not isinstance(self.subj, RDF_Star_Triple):
            return 1 + self.obj.level()    
        elif not isinstance(self.obj, RDF_Star_Triple):
            return 1 + self.subj.level()
        else:
            return 1 + max(self.subj.level(), self.obj.level())
        
    # Get the quoted triple(s) (one level down) in the RDF* triple
    def getQuotedTriples(self):
        quoted_triples = list()
        # Case where subject is a quoted triple
        if isinstance(self.subj, RDF_Star_Triple):
            quoted_triples.append(self.subj)
            if (not self.subj.isRDFTriple()):
                quoted_triples.extend(self.subj.getQuotedTriples())
        # Case where object is a quoted triple
        if isinstance(self.obj, RDF_Star_Triple):
            quoted_triples.append(self.obj)
            if (not self.obj.isRDFTriple()):
                quoted_triples.extend(self.obj.getQuotedTriples())
        return quoted_triples
        
    # Get the core facts from the RDF* triple
    def getDeepestQuotedTriples(self):
        deepest = list()
        for quoted in self.getQuotedTriples():
            if quoted.isRDFTriple():
                deepest.append(quoted)
        return deepest
    
    # Get the deepest triples. For regular RDF, just return the same one.
    # Part of unqualification algorithm
    def getDeepestTriples(self):
        if self.isRDFTriple():
            return [RDF_Star_Triple(self.subj, self.pred, self.obj)]
        else:
            deepest = list()
            if isinstance(self.subj, RDF_Star_Triple):
                deepest.extend(self.subj.getDeepestTriples())
            if isinstance(self.obj, RDF_Star_Triple):
                deepest.extend(self.obj.getDeepestTriples())
            return deepest
    
    # decompose RDF* triple
    # input: RDF* triple
    # output: set of RDF triples
    # Decompose an RDF* triple based on standard reification
    def decompose(self, star_format="n-triples"):
        if star_format == "csv":
            s_tag, p_tag, o_tag = s_flag, p_flag, o_flag
        else:
            s_tag, p_tag, o_tag = s_URI, p_URI, o_URI
        
        triples = list()
        if self.isRDFTriple():
            # So the given triple is an RDF triple itself
            triples.append(RDF_Star_Triple(self.subj, self.pred, self.obj))
            
        else:
            # Create a new triple template
            new_triple = RDF_Star_Triple(None, self.pred, None)
            
            if (isinstance(self.subj, RDF_Star_Triple)):
                # So the subject is an RDF* triple
                if str(self.subj) in bn_dict:
                    # Use existing blank node
                    blank = bn_dict[str(self.subj)]
                    
                else:
                    # Create blank node and add reference
                    blank = Blank_Node()
                    bn_dict[str(self.subj)] = blank
                
                    # Spawn some new triples
                    s_triple = RDF_Star_Triple(blank, s_tag, self.subj.subj)
                    p_triple = RDF_Star_Triple(blank, p_tag, self.subj.pred)
                    o_triple = RDF_Star_Triple(blank, o_tag, self.subj.obj)

                    # Decompose, then add to list of triples
                    triples.extend(s_triple.decompose())
                    triples.append(p_triple)
                    triples.extend(o_triple.decompose())
                
                new_triple.setSubject(blank)
                
            else:
                new_triple.setSubject(self.subj)
                
            if (isinstance(self.obj, RDF_Star_Triple)):
                # So the object is an RDF* triple
                if str(self.obj) in bn_dict:
                    # Use existing blank node
                    blank = bn_dict[str(self.obj)]
                
                else:
                    # Create blank node and add reference
                    blank = Blank_Node()
                    bn_dict[str(self.obj)] = blank

                    # Spawn some new triples
                    s_triple = RDF_Star_Triple(blank, s_tag, self.obj.subj)
                    p_triple = RDF_Star_Triple(blank, p_tag, self.obj.pred)
                    o_triple = RDF_Star_Triple(blank, o_tag, self.obj.obj)

                    # Decompose, then add to list of triples
                    triples.extend(s_triple.decompose())
                    triples.append(p_triple)
                    triples.extend(o_triple.decompose())
                
                new_triple.setObject(blank)
                
            else:
                new_triple.setObject(self.obj)
                
            triples.append(new_triple)
            
        return triples
        
    # Decompose an RDF* triple based on symmetrical shortcut algorithm
    def shortDecompose(self):
        triples = list()
        
        if self.isRDFTriple():
            # So the given triple is an RDF triple itself
            triples.append(RDF_Star_Triple(self.subj, self.pred, self.obj))
            
        elif (isinstance(self.subj, RDF_Star_Triple)):
            # So the subject is an RDF* triple
            
            # Spawn some new triples
            nested_triple = RDF_Star_Triple(self.subj.subj, self.subj.pred, self.subj.obj)
            external_triple_s = RDF_Star_Triple(self.subj.subj, self.subj.pred + "/" + self.pred, self.obj)
            external_triple_o = RDF_Star_Triple(self.subj.obj, self.subj.pred + "/" + self.pred, self.obj)

            # Decompose, then add to list of triples
            triples.extend(nested_triple.shortDecompose())
            triples.extend(external_triple_s.shortDecompose())
            triples.extend(external_triple_o.shortDecompose())
                
        elif (isinstance(self.obj, RDF_Star_Triple)):
            # So the object is an RDF* triple
            
            # Spawn some new triples
            nested_triple = RDF_Star_Triple(self.obj.subj, self.obj.pred, self.obj.obj)
            external_triple_s = RDF_Star_Triple(self.subj, self.pred + "/" + self.obj.pred, self.obj.subj)
            external_triple_o = RDF_Star_Triple(self.subj, self.pred + "/" + self.obj.pred, self.obj.obj)

            # Decompose, then add to list of triples
            triples.extend(nested_triple.shortDecompose())
            triples.extend(external_triple_s.shortDecompose())
            triples.extend(external_triple_o.shortDecompose())
                
        return triples
        
    # Decompose an RDF* triple based on asymmetrical shortcut algorithm
    def shortDecomposeV2(self):
        triples = list()
        
        if self.isRDFTriple():
            # So the given triple is an RDF triple itself
            triples.append(RDF_Star_Triple(self.subj, self.pred, self.obj))
            
        elif (isinstance(self.subj, RDF_Star_Triple)):
            # So the subject is an RDF* triple
            
            # Spawn some new triples
            nested_triple = RDF_Star_Triple(self.subj.subj, self.subj.pred, self.subj.obj)
            external_triple_s = RDF_Star_Triple(self.subj.subj, self.subj.pred + "/" + self.pred, self.obj)
            external_triple_o = RDF_Star_Triple(self.subj.obj, self.subj.pred + "^-1" + "/" + self.pred, self.obj)

            # Decompose, then add to list of triples
            triples.extend(nested_triple.shortDecomposeV2())
            triples.extend(external_triple_s.shortDecomposeV2())
            triples.extend(external_triple_o.shortDecomposeV2())
                
        elif (isinstance(self.obj, RDF_Star_Triple)):
            # So the object is an RDF* triple
            
            # Spawn some new triples
            nested_triple = RDF_Star_Triple(self.obj.subj, self.obj.pred, self.obj.obj)
            external_triple_s = RDF_Star_Triple(self.subj, self.pred + "/" + self.obj.pred, self.obj.subj)
            external_triple_o = RDF_Star_Triple(self.subj, self.pred + "/" + self.obj.pred + "^-1", self.obj.obj)

            # Decompose, then add to list of triples
            triples.extend(nested_triple.shortDecomposeV2())
            triples.extend(external_triple_s.shortDecomposeV2())
            triples.extend(external_triple_o.shortDecomposeV2())
                
        return triples
        
    def convertToTuple(self):    
        # Level 0
        if not isinstance(self.subj, RDF_Star_Triple) and not isinstance(self.obj, RDF_Star_Triple):
            return (self.subj, self.pred, self.obj)
        # Object is a triple
        elif not isinstance(self.subj, RDF_Star_Triple):
            return (self.subj, self.pred, self.obj.convertToTuple())
        # Subject is a triple
        elif not isinstance(self.obj, RDF_Star_Triple):
            return (self.subj.convertToTuple(), self.pred, self.obj)
        # Both subject and object are triples
        else:
            return (self.subj.convertToTuple(), self.pred, self.obj.convertToTuple())
        
    def __eq__(self, other):
        if not isinstance(other, RDF_Star_Triple):
            return False
        return self.subj == other.subj and self.pred == other.pred and self.obj == other.obj
        
    def __str__(self):
        return "(" + str(self.subj) + ", " + str(self.pred) + ", " + str(self.obj) + ")"
    
# Intermediate node object
class Blank_Node():
    
    def __init__(self, name=None):
        self.name = name
        
    def __str__(self):
        return "_:" + "bNode" + str(id(self)) # self.name
    
class RDF_Star_Graph():
    
    def __init__(self):
        self.triples_list = []
        
    # Add an RDF* triple to the knowledge graph
    def add(self, triple, copy=True):
        if isinstance(triple, tuple):
            # Triple is a tuple, Tuple should have three elements
            self.triples_list.append(RDF_Star_Triple(triple[0], triple[1], triple[2]))
            
        elif isinstance(triple, RDF_Star_Triple):
            if (copy):
                self.triples_list.append(RDF_Star_Triple(triple.subj, triple.pred, triple.obj))
            else:
                self.triples_list.append(triple)

    # Add list of triples to the knowledge graph          
    # For RDF* triples only, NO TUPLES, NO COPY YET
    def addAll(self, t_list):
        self.triples_list.extend(t_list)
    
    # Check if knowledge graph contains only RDF (not RDF*) triples
    def isRegularRDF(self):
        for triple in self.triples_list:
            if triple.level() != 0:
                return False
        return True
    
    # This is a single function which can perform any translation algorithm
    # given the name of the algorithm as a string input
    def performTranslationAlgo(self, algo, star_format="n-triples"):
        if algo == "unqualiification":
            return self.simplify()
        elif algo == "std_reification":
            return self.decompose(star_format=star_format)
        elif algo == "std_reification_plus":
            return self.convertToRegularRDF(star_format=star_format)
        elif algo == "shortcut_symmetric":
            return self.shortcutConvert()
        elif algo == "shortcut_asymmetric":
            return self.shortcutConvertV2()
        elif algo == "ext_reification_symmetric":
            return self.enhancedConvertV1(star_format=star_format)
        elif (algo == "ext_reification") or (algo == "extret"):
            return self.enhancedConvertV2(star_format=star_format)
        else:
            return None
    
    # Unqualiification algorithm
    def simplify(self):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            rdf.addAll(star_triple.getDeepestTriples())
            
        return rdf
    
    # Convert from RDF* to RDF using standard reification
    def decompose(self, star_format="n-triples"):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            if star_triple.isRDFTriple():
                # Add a copy of the triple itself
                rdf.add(star_triple, copy=True)
            else:
                # Decompose, then add them to the new graph
                decomposed = star_triple.decompose(star_format=star_format)
                rdf.addAll(decomposed)
        
        return rdf 
    
    # Convert from RDF* to RDF using standard reification + unqualification
    def convertToRegularRDF(self, star_format="n-triples"):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            if star_triple.isRDFTriple():
                # Add a copy of the triple itself
                rdf.add(star_triple, copy=True)
            else:
                # Decompose, then add them to the new graph
                decomposed = star_triple.decompose(star_format=star_format)
                rdf.addAll(decomposed)
                # Unqualify, then add them to the new graph
                simplified = star_triple.getDeepestTriples()
                rdf.addAll(simplified)
        
        return rdf            
    
    # Convert from RDF* to RDF using symmetrical shortcut algorithm
    def shortcutConvert(self):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            # Decompose, then add them to the new graph
            decomposed = star_triple.shortDecompose()
            rdf.addAll(decomposed)
        
        return rdf
    
    # Convert from RDF* to RDF using asymmetrical shortcut algorithm
    def shortcutConvertV2(self):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            # Decompose, then add them to the new graph
            decomposed = star_triple.shortDecomposeV2()
            rdf.addAll(decomposed)
        
        return rdf
    
    # Convert from RDF* to RDF using extended reification (symmetrical version)
    def enhancedConvertV1(self, star_format="n-triples"):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            if star_triple.isRDFTriple():
                # Add a copy of the triple itself
                rdf.add(star_triple, copy=True)
            else:
                # Decompose, then add them to the new graph
                decomposed = star_triple.decompose(star_format=star_format)
                extra = star_triple.shortDecompose()
                rdf.addAll(decomposed)
                rdf.addAll(extra)

        return rdf
    
    # Convert from RDF* to RDF using extended reification (asymmetrical version)
    # Aka ExtRet
    def enhancedConvertV2(self, star_format="n-triples"):
        rdf = RDF_Star_Graph()
        
        for star_triple in self:
            if star_triple.isRDFTriple():
                # Add a copy of the triple itself
                rdf.add(star_triple, copy=True)
            else:
                # Decompose, then add them to the new graph
                decomposed = star_triple.decompose(star_format=star_format)
                extra = star_triple.shortDecomposeV2()
                rdf.addAll(decomposed)
                rdf.addAll(extra)
        
        return rdf
    
    # Replace all old nodes containing certain values with new nodes
    def replaceAll(self, old, new):
        for triple in self.triples_list:
            triple.replaceAll(old, new)
            
    # Parse Tab-Separated-Values
    def parse(self, file_name):
        file = open(file_name, encoding='utf-8')
        read_file = csv.reader(file, delimiter="\t")
        
        row_num = 0
        for row in read_file:
            self.add(self.__parse_row(Buffer(row)))
            row_num += 1
            
        print("Number of RDF* triples parsed: ", row_num)

    # Parse each row in tsv file
    def __parse_row(self, buffer):
        storage = []

        # Each row is in list format
        # Triples must have three elements
        for _ in range(3):
            if buffer.current() == "<<":
                buffer.strip()  # Remove "<<"
                parsed = self.__parse_row(buffer) # Parse the nested triple
                storage.append(parsed)  # Add to storage
                buffer.strip()  # Remove ">>"
            else:
                storage.append(buffer.current()) # Add to storage
                buffer.strip()  # Remove element

        return (storage[0], storage[1], storage[2])
    
    def serialise(self, file_name):
        with open(file_name, 'w', encoding='utf-8', newline="") as out_file:
            writer = csv.writer(out_file, delimiter="\t")
            
            row_num = 0
            for triple in self.triples_list:
                writer.writerow(self.convertToNTXStyle(triple))
                row_num += 1
                
            print("Number of RDF triples serialised: ", row_num)
    
    def convertToNTXStyle(self, triple):
        ntx_list = list()
        if isinstance(triple.subj, RDF_Star_Triple):
            ntx_list.append("<<") # Indicate start of nested triple
            ntx_list.extend(self.convertToNTXStyle(triple.subj)[:-1]) # Add nested triple contents, but remove "."
            ntx_list.append(">>") # Indicate end of nested triple
        else:
            ntx_list.append(triple.subj)
        
        ntx_list.append(triple.pred)
        
        if isinstance(triple.obj, RDF_Star_Triple):
            ntx_list.append("<<")
            ntx_list.extend(self.convertToNTXStyle(triple.obj)[:-1])
            ntx_list.append(">>")
        else:
            ntx_list.append(triple.obj)
            
        ntx_list.append(".")
        
        return ntx_list
        
    def __str__(self):
        return str([str(elem) for elem in self.triples_list])
    
    def __iter__(self):
        return RDF_Star_Iterator(self)
    
class RDF_Star_Iterator(): # This class will allow the graph object to be iterable
    
    def __init__(self, rdf_star):
        self.rdf_star = rdf_star
        self.index = 0 # initialise index
        
    def __next__(self):
        if self.index < len(self.rdf_star.triples_list):
            result = self.rdf_star.triples_list[self.index]
            self.index += 1
            return result
        raise StopIteration
        
class Buffer():
    
    def __init__(self, row_values):
        self.row_values = row_values
        
    # Remove first element from buffer
    def strip(self):
        self.row_values = self.row_values[1:] 
        
    # Get the current first element from buffer
    def current(self):
        return self.row_values[0] 


'''
   The following functions are only available for RDF* triples with
   the following structures:
   E.g. RDF triples with format (s, p, o)
        RDF* triples with format ((s, p, o), p, o)
'''

# Parse triples from csv file
def parse_csv(file_name):
    file = open(file_name, encoding='utf-8')
    read_file = csv.reader(file, delimiter=",")
    graph = RDF_Star_Graph()
    
    for row in read_file:
        length = len(row)
        
        if length == 3:
            graph.add(RDF_Star_Triple(row[0], row[1], row[2]), copy=False)
        
        elif length > 3:
            for i in range(3, length, 2):
                graph.add(RDF_Star_Triple((row[0], row[1], row[2]), row[i], row[i+1]), copy=False)
                
    return graph

# Serialise triples to csv file
def serialise_csv(file_name, graph):
    with open(file_name, 'w', encoding='utf-8', newline="") as out_file:
        writer = csv.writer(out_file, delimiter=",")
        for triple in graph:
            if triple.isRDFTriple():
                writer.writerow([triple.subj, triple.pred, triple.obj])
            else:
                writer.writerow([triple.subj.subj, triple.subj.pred, triple.subj.obj, triple.pred, triple.obj])

# Get all entites and predicates
def get_entities_and_predicates(file_name):
    entities = set()
    predicates = set()
    
    file = open(file_name, encoding='utf-8')
    read_file = csv.reader(file, delimiter=",")
    
    for row in read_file:
        for i in range(len(row)):
            if i % 2 == 0:
                entities.add(row[i])
            else:
                predicates.add(row[i])
    
    file.close()
    
    return entities, predicates

# Pick random entities from csv file
def pick_random_entities(file_name, num_of_entities):
    entities, _ = get_entities_and_predicates(file_name)
    random_entities = random.choices(list(entities), k=num_of_entities)
    return random_entities

# Pick random entities from graph
def pick_random_entities_graph(graph, num_of_entities):
    entities = graph_entities(graph)
    random_entities = random.choices(entities, k=num_of_entities)
    return random_entities

# Generate a subgraph from the list of entities
def generate_subset(graph, entities_list):
    new_graph = RDF_Star_Graph()
    
    for triple in graph:
        if _triple_check(triple, entities_list):
            new_graph.add(triple)
            
    return new_graph

# Generate a subgraph from the list of entities, but put a cap on the number of 
# triples per entity
def generate_subset_limited(graph, entities_list, limit):
    entities_count = dict()
    new_graph = RDF_Star_Graph()
    
    for triple in graph:
        if _triple_check(triple, entities_list):
            # Check limit before adding
            triple_ents = triple_entities(triple)
            
            for ent in triple_ents:
                if (ent in entities_list) and (entities_count.setdefault(ent, 0) < limit):
                    
                    # Add to graph only if not all limits are reached
                    # Entity needs to be in the list
                    new_graph.add(triple)
                    
                    # Add to limit count of that particular entity
                    # Allow space in other entities
                    if ent in entities_count:
                        entities_count[ent] += 1
                    else:
                        entities_count[ent] = 1
                        
                    break
    
    return new_graph

# Do sampling process twice with cap of number of triples per entity
def double_sampling(graph, first_entity_count, first_stmt_limit, second_entity_count, second_stmt_limit):
    print("Picking initial set of entities ...")
    init_entities = pick_random_entities_graph(graph, first_entity_count)
    print("Generating first subset ...")
    first_subset = generate_subset_limited(graph, init_entities, first_stmt_limit)
    
    print("Picking entities within the subset ...")
    snd_entities = pick_random_entities_graph(first_subset, second_entity_count)
    print("Generating new subset ...")
    sec_subset = generate_subset_limited(graph, snd_entities, second_stmt_limit)
    
    return sec_subset

# Do sampling process twice, but without the cap on number of triples per entity
def double_sampling_full(graph, first_entity_count, second_entity_count):
    print("Picking initial set of entities ...")
    init_entities = pick_random_entities_graph(graph, first_entity_count)
    print("Generating first subset ...")
    first_subset = generate_subset(graph, init_entities)
    
    print("Picking entities within the subset ...")
    snd_entities = pick_random_entities_graph(first_subset, second_entity_count)
    print("Generating new subset ...")
    sec_subset = generate_subset(graph, union(init_entities, snd_entities))
    
    return sec_subset

# Check if the triple contains entities that are in the list of entities
def _triple_check(triple, entities_list):
    # Case 1: Single-level RDF* triple
    if triple.isRDFTriple():
        return (triple.subj in entities_list) or (triple.obj in entities_list)
    
    # Case 2: Subject is RDF* triple, object is not RDF* triple
    elif isinstance(triple.subj, RDF_Star_Triple) and not isinstance(triple.obj, RDF_Star_Triple):
        return _triple_check(triple.subj, entities_list) or (triple.obj in entities_list)
    
    # Case 3: Object is RDF*, subject is not RDF*
    elif not isinstance(triple.subj, RDF_Star_Triple) and isinstance(triple.obj, RDF_Star_Triple):
        return (triple.subj in entities_list) or _triple_check(triple.obj, entities_list)
    
    # Case 4: Both subject and object are RDF* triples
    elif isinstance(triple.subj, RDF_Star_Triple) and isinstance(triple.obj, RDF_Star_Triple):
        return _triple_check(triple.subj, entities_list) or _triple_check(triple.obj, entities_list)

# Count the number of entities in a graph
def entity_count(graph):    
    return len(graph_entities(graph))

def graph_entities(graph):
    entities = []
    
    for triple in graph:
        for ent in triple_entities(triple):
            if not (ent in entities):
                entities.append(ent)
    
    return entities

# Helper function to get list of entities in a triple
def triple_entities(triple):
    entities = []
    if not isinstance(triple.subj, RDF_Star_Triple):
        # So the subject is not an RDF* triple
        if not (str(triple.subj) in entities):
            entities.append(str(triple.subj))
    else:
        for ent in triple_entities(triple.subj):
            if not (ent in entities):
                entities.append(ent)
    
    if not isinstance(triple.obj, RDF_Star_Triple):
        # So the object is not an RDF* triple
        if not (str(triple.obj) in entities):
            entities.append(str(triple.obj))
    else:
        for ent in triple_entities(triple.obj):
            if not (ent in entities):
                entities.append(ent)
    
    return entities

# Define relationship count
def relation_count(graph):
    return len(graph_relations(graph))
    
def graph_relations(graph):
    relations = []
    
    for triple in graph:
        for rel in triple_relations(triple):
            if not (rel in relations):
                relations.append(rel)
    
    return relations
    
# Helper function to get list of relations in a triple
def triple_relations(triple):
    relations = [str(triple.pred)]
    
    if isinstance(triple.subj, RDF_Star_Triple):
        for rel in triple_relations(triple.subj):
            if not (rel in relations):
                relations.append(rel)
    
    if isinstance(triple.obj, RDF_Star_Triple):
        for rel in triple_relations(triple.obj):
            if not (rel in relations):
                relations.append(rel)
    
    return relations

def union(list1, list2):
    return list(set(list1) | set(list2))

def total_entity_count(train, test):
    return len(union(graph_entities(train), graph_entities(test)))

def total_relation_count(train, test):
    return len(union(graph_relations(train), graph_relations(test)))

# Count the number of unique triples
def unique_triples_count(graph):
    return len(graph_triples(graph))

# Helper function
def graph_triples(graph):
    return set(list(map(str, graph)))