import csv

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


