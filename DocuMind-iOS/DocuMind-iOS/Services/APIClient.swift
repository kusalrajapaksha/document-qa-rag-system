//
//  APIClient.swift
//  DocuMind-iOS
//
//  Created by Kusal on 2026-10-22.
//

import Foundation

enum APIError: LocalizedError {
    case invalidResponse
    case serverError(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The server returned an invalid response."
        case .serverError(let message):
            return message
        }
    }
}

final class APIClient {
    static let shared = APIClient()

    // For the iOS Simulator running on the same Mac.
    private let baseURL = URL(
        string: "http://127.0.0.1:8000"
    )!

    private let session = URLSession.shared

    private init() {}

    
    private func validate(
        _ data: Data,
        response: URLResponse
    ) throws {
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200..<300).contains(http.statusCode) else {
            let detail = (
                try? JSONSerialization.jsonObject(with: data)
                    as? [String: Any]
            )?["detail"] as? String

            throw APIError.serverError(
                detail ?? "Request failed (\(http.statusCode))."
            )
        }
    }

    func fetchDocuments() async throws -> [DocumentItem] {
        let url = baseURL.appendingPathComponent("documents")
        let (data, response) = try await session.data(from: url)
        try validate(data, response: response)

        return try JSONDecoder()
            .decode(DocumentListResponse.self, from: data)
            .documents
    }

    func uploadPDF(
        data: Data,
        filename: String
    ) async throws -> IndexDocumentResponse {
        let url = baseURL.appendingPathComponent("documents/index")
        let boundary = UUID().uuidString

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(
            "multipart/form-data; boundary=\(boundary)",
            forHTTPHeaderField: "Content-Type"
        )

        var body = Data()
        body.appendUTF8("--\(boundary)\r\n")
        body.appendUTF8(
            "Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n"
        )
        body.appendUTF8("Content-Type: application/pdf\r\n\r\n")
        body.append(data)
        body.appendUTF8("\r\n--\(boundary)--\r\n")

        let (responseData, response) = try await session.upload(
            for: request,
            from: body
        )

        try validate(responseData, response: response)

        return try JSONDecoder().decode(
            IndexDocumentResponse.self,
            from: responseData
        )
    }

    func ask(
        question: String,
        documentID: String
    ) async throws -> AskDocumentResponse {
        let url = baseURL.appendingPathComponent("document/ask")

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue(
            "application/x-www-form-urlencoded",
            forHTTPHeaderField: "Content-Type"
        )

        var components = URLComponents()
        components.queryItems = [
            URLQueryItem(name: "question", value: question),
            URLQueryItem(name: "document_id", value: documentID)
        ]

        request.httpBody = components.percentEncodedQuery?
            .data(using: .utf8)

        let (data, response) = try await session.data(for: request)
        try validate(data, response: response)

        return try JSONDecoder().decode(
            AskDocumentResponse.self,
            from: data
        )
    }

    func deleteDocument(id: String) async throws {
        let url = baseURL
            .appendingPathComponent("documents")
            .appendingPathComponent(id)
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        let (data, response) = try await session.data(for: request)
        try validate(data, response: response)
    }
    
}

private extension Data {
    mutating func appendUTF8(_ string: String) {
        append(Data(string.utf8))
    }
}

