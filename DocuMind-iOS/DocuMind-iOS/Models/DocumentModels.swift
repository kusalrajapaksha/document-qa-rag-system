//
//  DocumentModels.swift
//  DocuMind-iOS
//
//  Created by Kusal on 2026-10-22.
//

import Foundation

struct DocumentListResponse: Decodable {
    let documentCount: Int
    let documents: [DocumentItem]

    enum CodingKeys: String, CodingKey {
        case documentCount = "document_count"
        case documents
    }
}

struct DocumentItem: Decodable, Identifiable {
    let documentID: String
    let filename: String
    let chunkCount: Int
    let pageCount: Int

    var id: String { documentID }

    enum CodingKeys: String, CodingKey {
        case documentID = "document_id"
        case filename
        case chunkCount = "chunk_count"
        case pageCount = "page_count"
    }
}

struct IndexDocumentResponse: Decodable {
    let documentID: String
    let filename: String?
    let pageCount: Int
    let chunkCount: Int
    let status: String

    enum CodingKeys: String, CodingKey {
        case documentID = "document_id"
        case filename
        case pageCount = "page_count"
        case chunkCount = "chunk_count"
        case status
    }
}

struct AskDocumentResponse: Decodable {
    let question: String
    let answer: String
    let sources: [DocumentSource]
}

struct DocumentSource: Decodable, Identifiable {
    let documentID: String
    let pageNumber: Int
    let chunkID: Int
    let similarityScore: Double
    let text: String

    var id: String {
        "\(documentID)-\(chunkID)"
    }

    enum CodingKeys: String, CodingKey {
        case documentID = "document_id"
        case pageNumber = "page_number"
        case chunkID = "chunk_id"
        case similarityScore = "similarity_score"
        case text
    }
}

