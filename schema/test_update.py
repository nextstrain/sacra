import os, re, time, datetime, csv, sys, json
import numpy as np
import rethinkdb as r

# Parameters
replicates = 100
strain_count = 1000
samples_per_strain = 10
sequences_per_sample = 10
seqlength = 20000

# Load data
with open('schema_zika.json') as json_data:
    relational_data = json.load(json_data)

with open('schema_zika_nested_dict.json') as json_data:
    nested_data = json.load(json_data)

# Connect to RethinkDB
rethink_host = 'localhost'
auth_key = ''
conn = r.connect(host=rethink_host, port=28015, auth_key=auth_key)

# Create db, create tables and create secondary indexes, only run on the first go
# r.db_create('relational').run(conn)
# r.db_create('nested').run(conn)
# r.db('relational').table_create('strains').run(conn)
# r.db('relational').table_create('samples').run(conn)
# r.db('relational').table_create('sequences').run(conn)
# r.db('relational').table_create('attributions').run(conn)
# r.db('nested').table_create('strains').run(conn)
# r.db('nested').table_create('attributions').run(conn)
# r.db('relational').table('samples').index_create('strain_name').run(conn)
# r.db('relational').table('sequences').index_create('strain_name').run(conn)
# r.db('relational').table('sequences').index_create('sample_name').run(conn)
# r.db('relational').table('samples').index_wait('strain_name').run(conn)
# r.db('relational').table('sequences').index_wait('strain_name').run(conn)
# r.db('relational').table('sequences').index_wait('sample_name').run(conn)

# Reset data
print("Reset data")
r.db('relational').table('strains').delete().run(conn)
r.db('relational').table('samples').delete().run(conn)
r.db('relational').table('sequences').delete().run(conn)
r.db('relational').table('attributions').delete().run(conn)
r.db('nested').table('strains').delete().run(conn)
r.db('nested').table('attributions').delete().run(conn)

# Add data
print("Load data from schema")
for strain in relational_data["strains"]:
    call = r.db('relational').table('strains').insert(strain).run(conn)
for sample in relational_data["samples"]:
    call = r.db('relational').table('samples').insert(sample).run(conn)
for sequence in relational_data["sequences"]:
    call = r.db('relational').table('sequences').insert(sequence).run(conn)
for attribution in relational_data["attributions"]:
    call = r.db('relational').table('attributions').insert(attribution).run(conn)
for strain in nested_data["strains"]:
    call = r.db('nested').table('strains').insert(strain).run(conn)
for attribution in nested_data["attributions"]:
    call = r.db('nested').table('attributions').insert(attribution).run(conn)

# Make sequences big
print("Make sequences big")
bigseq = "".join(['a' for x in range(0, seqlength)])
call = r.db('relational').table('sequences').get('USVI/1/2016|VI1.1|1').update({"sequence": bigseq}).run(conn)
call = r.db('relational').table('sequences').get('USVI/1/2016|VI1.2|1').update({"sequence": bigseq}).run(conn)
call = r.db('relational').table('sequences').get('DominicanRepublic/2016/PD|PD1|KU853012').update({"sequence": bigseq}).run(conn)
call = r.db('relational').table('sequences').get('DominicanRepublic/2016/PD|PD2|KU853013').update({"sequence": bigseq}).run(conn)
call = (r.db('nested').table('strains')
    .get('USVI/1/2016')
    .update({
        'samples': {
            'USVI/1/2016|VI1.1': {
                'sequences': {
                    'USVI/1/2016|VI1.1|1' : {'sequence': bigseq}
                }
            },
            'USVI/1/2016|VI1.2': {
                'sequences': {
                    'USVI/1/2016|VI1.2|1' : {'sequence': bigseq}
                }
            }
        }
    }).run(conn))
call = (r.db('nested').table('strains')
    .get('DominicanRepublic/2016/PD')
    .update({
        'samples': {
            'DominicanRepublic/2016/PD|PD1': {
                'sequences': {
                    'DominicanRepublic/2016/PD|PD1|KU853012' : {'sequence': bigseq}
                }
            },
            'DominicanRepublic/2016/PD|PD2': {
                'sequences': {
                    'DominicanRepublic/2016/PD|PD2|KU853013' : {'sequence': bigseq}
                }
            }
        }
    }).run(conn))

# Adding documents
print("Adding documents")

print("Adding strains to relational db")
docs = []
doc = r.db('relational').table('strains').get('USVI/1/2016').run(conn)
for x in range(0, strain_count):
    doc['id'] = str(x)
    doc['strain_name'] = str(x)
    doc['samples'] = []
    for y in range(0, samples_per_strain):
        doc['samples'].append(str(x)+"|"+str(y))
    docs.append(doc)
call = r.db('relational').table('strains').insert(docs).run(conn)

print("Adding samples to relational db")
docs = []
doc = r.db('relational').table('samples').get('USVI/1/2016|VI1.1').run(conn)
for x in range(0, strain_count):
    for y in range(0, samples_per_strain):
        doc['id'] = str(x)+"|"+str(y)
        doc['strain_name'] = str(x)
        doc['sample_name'] = str(x)+"|"+str(y)
        doc['sequences'] = []
        for z in range(0, sequences_per_sample):
            doc['sequences'].append(str(x)+"|"+str(y)+"|"+str(z))
        docs.append(doc)
call = r.db('relational').table('samples').insert(docs).run(conn)

print("Adding sequences to relational db")
docs = []
doc = r.db('relational').table('sequences').get('USVI/1/2016|VI1.1|1').run(conn)
for x in range(0, strain_count):
    for y in range(0, samples_per_strain):
        for z in range(0, sequences_per_sample):
            doc['id'] = str(x)+"|"+str(y)+"|"+str(z)
            doc['strain_name'] = str(x)
            doc['sample_name'] = str(x)+"|"+str(y)
            doc['sequence_accession'] = str(x)+"|"+str(y)+"|"+str(z)
            docs.append(doc)
call = r.db('relational').table('sequences').insert(doc).run(conn)

print("Adding strains to nested db")
docs = []
doc = r.db('nested').table('strains').get('USVI/1/2016').run(conn)
for x in range(0, strain_count):
    doc['id'] = str(x)
    docs.append(doc)
call = r.db('nested').table('strains').insert(doc).run(conn)

# call = r.db('relational').table('strains').count().run(conn)
# print(call)

# call = (r.db('nested').table('strains')
#     .get('USVI/1/2016')
#     .update(
#         {'samples': {'USVI/1/2016|VI1.1': {'ct' : "test"}}}
#     ).run(conn))


# Check sequence documents
# call = r.db('relational').table('sequences').get('USVI/1/2016|VI1.1|1').run(conn)
# print(call)

# call = r.db('nested').table('strains').get('DominicanRepublic/2016/PD').run(conn)
# print json.dumps(call, indent=2)

# Updates
print("Testing write performance")

# Updating sample attribute
print("Update sample attribute ct")

# Relational update
start_time = time.time()
for x in range(0,replicates):
    call = r.db('relational').table('samples').get('USVI/1/2016|VI1.1').update({"ct": str(x)}, durability="soft").run(conn)
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("relational updates per second: %.1f" % float(1/elapsed))

# Nested update
start_time = time.time()
for x in range(0,replicates):
    call = (r.db('nested').table('strains')
        .get('USVI/1/2016')
        .update(
            {'samples': {'USVI/1/2016|VI1.1': {'ct' : str(x)}}},
            durability="soft"
        )
        .run(conn))
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("nested updates per second: %.1f" % float(1/elapsed))

# Updating sequence attribute
print("Update sequence attribute sequence_segment")

# Relational update
start_time = time.time()
for x in range(0,replicates):
    call = r.db('relational').table('sequences').get('USVI/1/2016|VI1.1|1').update({"sequence_segment": str(x)}, durability="soft").run(conn)
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("relational updates per second: %.1f" % float(1/elapsed))

# Nested update
start_time = time.time()
for x in range(0,replicates):
    call = (r.db('nested').table('strains')
        .get('USVI/1/2016')
        .update({
            'samples': {
                'USVI/1/2016|VI1.1': {
                    'sequences': {
                        'USVI/1/2016|VI1.1|1' : {'sequence_segment': str(x)}
                    }
                }
            }
        }, durability="soft")
        .run(conn))
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("nested updates per second: %.1f" % float(1/elapsed))

# Testing read performance
print("Testing read performance")
print("Get all sequence attribute sequence_segment associated with strain USVI/1/2016")

# Gather relational
start_time = time.time()
for x in range(0,replicates):
    cursor = r.db('relational').table('strains').get_all('USVI/1/2016').eq_join(
        'id',
        r.db('relational').table('sequences'),
        index='strain_name'
    ).zip()['sequence_segment'].run(conn)
    # print json.dumps(list(cursor), indent=2)
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("relational reads per second: %.1f" % float(1/elapsed))

# Gather nested
start_time = time.time()
for x in range(0,replicates):
    call = (r.db('nested').table('strains').get('USVI/1/2016').do(
        lambda strain: strain['samples'].values().map(
            lambda sample: sample['sequences'].values().map(
                lambda sequence: sequence['sequence_segment']
            )
        )
        ).run(conn))
    flattened_list = [y for x in call for y in x]
    # print json.dumps(flattened_list, indent=2)
end_time = time.time()
elapsed = (end_time - start_time)/float(replicates)
print("nested reads per second: %.1f" % float(1/elapsed))
