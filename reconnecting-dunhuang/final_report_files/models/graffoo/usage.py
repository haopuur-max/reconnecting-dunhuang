"""Class-level usage of every property in the final RDF: (subject class, property, object class or datatype)."""
from rdflib import Graph, RDF, Literal, URIRef
from paths import TTL
from collections import Counter
G = Graph().parse(TTL)
NM = G.namespace_manager
q = lambda u: NM.normalizeUri(u)
def classes(n):
    if isinstance(n, Literal):
        return {q(n.datatype) if n.datatype else ('rdf:langString' if n.language else 'xsd:string')}
    c = {q(t) for t in G.objects(n, RDF.type)}
    return c or {'(external IRI)'}
def usage():
    u = Counter()
    for s, p, o in G:
        if p == RDF.type: continue
        for cs in classes(s):
            for co in classes(o):
                u[(cs, q(p), co)] += 1
    return u
if __name__ == '__main__':
    for k, v in sorted(usage().items(), key=lambda x: (x[0][1], x[0][0])): print(v, *k)
