# -*- coding: utf-8 -*-

import FWCore.ParameterSet.Config as cms

from RecoJets.Configuration.RecoPFJets_cff import ak4PFJets, ak4PFJetsCHS
from RecoJets.Configuration.RecoGenJets_cff import ak4GenJets
from RecoJets.JetProducers.SubJetParameters_cfi import SubJetParameters
from RecoJets.JetProducers.PFJetParameters_cfi import *
from RecoJets.JetProducers.GenJetParameters_cfi import *
from RecoJets.JetProducers.AnomalousCellParameters_cfi import *
from RecoJets.JetProducers.CATopJetParameters_cfi import *
from PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff import *
from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import selectedPatJets
from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection

## Modified version of jetToolBox from https://github.com/cms-jet/jetToolbox 
## Options for PUMethod: Puppi, CS, SK, CHS
def jetToolbox( proc, jetType, jetSequence,PUMethod=''):
	JETCorrPayload='None'
	JETCorrLevels = [ 'None' ]
	#JECLevels = [ 'L1Offset', 'L1FastJet', 'L1JPTOffset', 'L2Relative', 'L3Absolute', 'L5Falvour', 'L7Parton' ]

	algorithm='AntiKt' # CambridgeAachen' , 'Kt'
	size = jetType[-1:] #[-1:] takes the last char from string 'akX'
	jetSize = float('0.'+jetType[-1:]) 
	jetALGO = jetType.upper()
	jetalgo = jetType.lower()
      
	print 'Running processes with: '+str(jetALGO)+' PF '+PUMethod+' jet algorithm with radius parameter '+str(jetSize)

	JETCorrPayload = 'AK'+size+'PFchs'
	#JETCorrLevels = ['L1FastJet', 'L2Relative', 'L3Absolute']
	JETCorrLevels = [] #No JEC corrections
	JEC = ( JETCorrPayload, JETCorrLevels , 'None')


	#################################################################################
	####### Toolbox start 
	#################################################################################

	jetSeq = cms.Sequence()

	genParticlesLabel = 'genParticles'
	pvLabel = 'offlinePrimaryVertices'
	svLabel = 'inclusiveSecondaryVertices'

	proc.load('RecoJets.Configuration.GenJetParticles_cff')
	proc.load('CommonTools.ParticleFlow.pfNoPileUpJME_cff')
	setattr( proc, jetalgo+'GenJetsNoNu', ak4GenJets.clone( src = 'genParticlesForJetsNoNu', rParam = jetSize, jetAlgorithm = algorithm ) ) 
	jetSeq += getattr(proc, jetalgo+'GenJetsNoNu' )
	####  Creating PATjets
	if( PUMethod=='CHS') :
	  setattr( proc, jetalgo+'PFJetsCHS', ak4PFJets.clone( rParam = jetSize, jetAlgorithm = algorithm ) ) 
	  jetSeq += getattr(proc, jetalgo+'PFJetsCHS' )

	  setattr( proc, jetalgo+'PFJetsCHS', 
			  ak4PFJetsCHS.clone( 
				  doAreaFastjet = True, 
				  rParam = jetSize, 
				  jetAlgorithm = algorithm ) ) 
	  jetSeq += getattr(proc, jetalgo+'PFJetsCHS' )
	
	else :
	  setattr( proc, jetalgo+'PFJets', ak4PFJets.clone( rParam = jetSize, jetAlgorithm = algorithm ) ) 
	  jetSeq += getattr(proc, jetalgo+'PFJets' )

	  setattr( proc, jetalgo+'PFJets', 
			  ak4PFJets.clone( 
				  doAreaFastjet = True, 
				  rParam = jetSize, 
				  jetAlgorithm = algorithm ) ) 
	  jetSeq += getattr(proc, jetalgo+'PFJets' )
	  PUMethod=''

	addJetCollection(
			proc,
			labelName = jetALGO+'PF'+PUMethod,
			jetSource = cms.InputTag( jetalgo+'PFJets'+PUMethod),
			algo = jetalgo,
			rParam = jetSize,
			jetCorrections =  JEC, #( 'AK'+size+'PFchs', cms.vstring( ['L1FastJet', 'L2Relative', 'L3Absolute']), 'None'),
			pfCandidates = cms.InputTag( 'particleFlow' ),  #'packedPFCandidates'),
			svSource = cms.InputTag( svLabel ),   #'slimmedSecondaryVertices'),
			genJetCollection = cms.InputTag( jetalgo+'GenJetsNoNu'),
			pvSource = cms.InputTag( pvLabel ), #'offlineSlimmedPrimaryVertices'),
			) 

	getattr( proc, 'patJetCorrFactors'+jetALGO+'PF'+PUMethod ).primaryVertices = pvLabel  #'offlineSlimmedPrimaryVertices' 
	getattr(proc,'patJetPartons').particles = cms.InputTag( genParticlesLabel ) #'prunedGenParticles')
	setattr(proc, 'selectedPatJets'+jetALGO+'PF'+PUMethod, selectedPatJets.clone( src = 'patJets'+jetALGO+'PF'+PUMethod ) )
	setattr(proc, jetSequence, jetSeq)




# -*- coding: utf-8 -*-
import FWCore.ParameterSet.Config as cms

process = cms.Process("Ntuplizer")
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#! Conditions
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.EventContent.EventContent_cff")
process.load('Configuration.StandardSequences.Geometry_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('RecoJets.Configuration.GenJetParticles_cff')
process.load('RecoJets.Configuration.RecoGenJets_cff')

process.GlobalTag.globaltag = "PHYS14_25_V2::All"


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#! Input
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  
                                    
inFiles = cms.untracked.vstring(
'file:///mnt/storage/gflouris/08C07BB6-376F-E411-BE9F-C4346BC7EE18.root' 
#'file:///afs/cern.ch/work/g/gflouris/public/SMPJ_AnalysisFW/08C07BB6-376F-E411-BE9F-C4346BC7EE18.root' 
   )
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))
process.source = cms.Source("PoolSource", fileNames = inFiles )

jetToolbox( process, 'ak4', 'ak4JetSubs','CHS') 
jetToolbox( process, 'ak4', 'ak7JetSubs') 

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#! Services
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.load('CommonTools.UtilAlgos.TFileService_cfi')
process.TFileService.fileName=cms.string('MC_ProcessedTreeProducer_2.root')


process.ak4 =  cms.EDAnalyzer('ProcessedTreeProducer',
	## jet collections ###########################
	pfjets          = cms.InputTag('selectedPatJetsAK4PF'),
	pfjetschs       = cms.InputTag('selectedPatJetsAK4PFCHS'),
	## MET collection ####
	pfmet           = cms.InputTag('pfMet'),
	genjets         = cms.untracked.InputTag('ak4GenJets'),
	## database entry for the uncertainties ######
	PFPayloadName   = cms.string(''),
	PFPayloadNameCHS= cms.string(''),
	CaloPayloadName = cms.string(''),
	jecUncSrc       = cms.string(''),
	jecUncSrcCHS    = cms.string(''), 
	jecUncSrcNames  = cms.vstring(''),
	## set the conditions for good Vtx counting ##
	offlineVertices = cms.InputTag('goodOfflinePrimaryVertices'),
	goodVtxNdof     = cms.double(4), 
	goodVtxZ        = cms.double(24),
	## rho #######################################
	srcCaloRho      = cms.InputTag('fixedGridRhoFastjetAll'),
	srcPFRho        = cms.InputTag('fixedGridRhoFastjetAllCalo'),
	srcPU           = cms.untracked.InputTag('addPileupInfo'),
	## preselection cuts #########################
	maxY            = cms.double(5.0), 
	minPFPt         = cms.double(20),
	minPFFatPt      = cms.double(10),
	maxPFFatEta     = cms.double(2.5),
	minNPFJets      = cms.int32(1),
	minGenPt        = cms.untracked.double(20),
	minJJMass       = cms.double(-1),
	isMCarlo        = cms.untracked.bool(True),
	useGenInfo      = cms.untracked.bool(True),
	## trigger ###################################
	printTriggerMenu = cms.untracked.bool(True),
	processName     = cms.string('HLT'),
	triggerName     = cms.vstring('HLT_PFJet260_v1'),
	triggerResults  = cms.InputTag("TriggerResults","","HLT"),
	triggerEvent    = cms.InputTag("hltTriggerSummaryAOD","","HLT"),
	## jec services ##############################
	#pfjecService    = cms.string('ak7PFL1FastL2L3Residual'),
	#calojecService  = cms.string('ak7CaloL1FastL2L3Residual')
)


jetToolbox( process, 'ak8', 'ak5JetSubs','CHS') 
jetToolbox( process, 'ak8', 'ak7JetSubs') 

process.ak8 = process.ak4.clone(
	pfjets          = cms.InputTag('selectedPatJetsAK8PF'),
	pfjetschs       = cms.InputTag('selectedPatJetsAK8PFCHS'),
	## MET collection ####
	pfmet           = cms.InputTag('pfMet'),
	genjets         = cms.untracked.InputTag('ak8GenJets'),
)

jetToolbox( process, 'ak7', 'ak5JetSubs','CHS') 
jetToolbox( process, 'ak7', 'ak7JetSubs') 

process.ak7GenJets = process.ak5GenJets.clone()
process.ak7GenJets.rParam = cms.double(0.7)

process.ak7 = process.ak4.clone(
	pfjets          = cms.InputTag('selectedPatJetsAK7PF'),
	pfjetschs       = cms.InputTag('selectedPatJetsAK7PFCHS'),
	## MET collection ####
	pfmet           = cms.InputTag('pfMet'),
	genjets         = cms.untracked.InputTag('ak7GenJets'),
)

jetToolbox( process, 'ak5', 'ak5JetSubs','CHS') 
jetToolbox( process, 'ak5', 'ak7JetSubs') 

process.ak5GenJets = process.ak5GenJets.clone()
process.ak5GenJets.rParam = cms.double(0.5)

process.ak5 = process.ak4.clone(
	pfjets          = cms.InputTag('selectedPatJetsAK5PF'),
	pfjetschs       = cms.InputTag('selectedPatJetsAK5PFCHS'),
	## MET collection ####
	pfmet           = cms.InputTag('pfMet'),
	genjets         = cms.untracked.InputTag('ak5GenJets'),
)


process.p = cms.Path( process.ak4*process.ak5*process.ak7*process.ak8 )


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#! Output and Log
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )
process.options.allowUnscheduled = cms.untracked.bool(True)

process.output = cms.OutputModule("PoolOutputModule",                                                                                                                                                     
                                  #outputCommands = cms.untracked.vstring('drop *','keep *_puppi_*_*'),
                                  outputCommands = cms.untracked.vstring('keep *'),
                                  fileName       = cms.untracked.string ("Output.root")                                                                                                                   
)
# schedule definition                                                                                                       
#process.outpath  = cms.EndPath(process.out) 
