#!/usr/bin/env python
import geometry
import gen_utils

VERTEX_LINE_MARKER = "v "
FACE_LINE_MARKER = "f "

class SMFModel:
	#List of vertices (point objects)
	vertices = []
	#List of faces (polygon objects)
	faces = []
	
	#Need to maintain relationship between vertices and faces
	#Python's "everything is a reference" doesn't really work for this
	#If we change a vertex, the face referencing that vertex is not updated
	#[ F1:(v1 index, v2 index, v3 index), F2:(v1 index, v2 index, v3 index) ... ]
	face_vertex_indices = []
	
	def __init__(self):
		#List of vertices (points)
		self.vertices = []
		#List of faces
		self.faces = []
		#Relationship between vertices
		self.face_vertex_indices = []
		
	#Rebuild faces after modifing vertices
	def rebuild_faces_list(self):
		#List of faces cleared
		self.faces = []
		#Loop over list of faces as vertex indices
		#Create a new face object out of the vertices list
		for vertex_indices in self.face_vertex_indices:
			v1_index = vertex_indices[0]
			v2_index = vertex_indices[1]
			v3_index = vertex_indices[2]
			new_f = None
			new_f = geometry.Polygon()
			new_f.vertices = new_f.vertices + [ self.vertices[v1_index],self.vertices[v2_index],self.vertices[v3_index] ]
			self.faces = self.faces + [new_f]
	
	#Apply transform to all vertices
	def apply_transform(self, transform_matrix):
		#Loop over all vertices
		for vertex in self.vertices:
			#Then apply transform to each vertex
			vertex.apply_transform(transform_matrix)
		#Rebuild faces after modifing vertices
		self.rebuild_faces_list()
			
	#Populate from file
	def build_from_file(self,filename):
		#Open file
		f = open(filename,'r')
		
		#Get all lines
		lines=f.readlines()
		
		#Loop over lines
		for line in lines:
			toks = gen_utils.split_and_remove(line," ","")
			#Vertex line
			if VERTEX_LINE_MARKER in line:
				new_v = None
				new_v = geometry.Point()
				new_v.x=float(toks[1])
				new_v.y=float(toks[2])
				new_v.z=float(toks[3])
				self.vertices = self.vertices + [new_v]
			#Face line
			elif FACE_LINE_MARKER in line:
				new_f = None
				new_f = geometry.Polygon()
				v1_index = int(toks[1]) - 1
				v2_index = int(toks[2]) - 1
				v3_index = int(toks[3]) - 1
				new_f.vertices = new_f.vertices + [ self.vertices[v1_index],self.vertices[v2_index],self.vertices[v3_index] ]
				self.faces = self.faces + [new_f]
				#Relationship between vertices
				self.face_vertex_indices = self.face_vertex_indices + [(v1_index,v2_index,v3_index)]
			else:
				#Ignore unknown line
				continue
		
		f.close()
			
		
	#Equality operator	
	def __eq__(self, obj):
		#Check that vertices list is same length
		if len(self.vertices) != len(obj.vertices):
			return False
			
		#Check each vertex is equal
		for i in range(0,len(self.vertices)):
			if self.vertices[i] != obj.vertices[i]:
				return False
				
		#Check face list
		if len(self.faces) != len(obj.faces):
			return False
			
		#Check each face is equal
		for i in range(0,len(self.faces)):
			if self.faces[i] != obj.faces[i]:
				return False
				
		#All parts equal
		return True
		
	def __ne__(self, obj):
		return not( self.__eq__(obj) )
		
	#To string operator
	def __str__(self):
		#Print each face
		rv = ""
		for i in range(0,len(self.faces)):
			f = self.faces[i]
			s = str(f)
			rv = rv + "F" + str(i) + s + "\n"
		return rv

#Get smf models from multiple files
def get_smf_models(smf_files):
	all_models = []
	for smf_file in smf_files:
		model = get_smf_model(smf_file)
		all_models = all_models + [model]
	return all_models		
	
#Get smf model from single file
def get_smf_model(smf_file):
	model = SMFModel()
	model.build_from_file(smf_file)
	return model
