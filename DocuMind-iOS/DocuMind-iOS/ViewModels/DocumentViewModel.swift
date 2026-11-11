//
//  DocumentViewModel.swift
//  DocuMind-iOS
//
//  Created by Kusal on 2026-10-22.
//

import Foundation
import SwiftUI
import Combine

@MainActor
final class DocumentViewModel: ObservableObject {
    @Published var documents: [DocumentItem] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedDocument: DocumentItem?

    func loadDocuments() async {
        isLoading = true
        defer { isLoading = false }

        do {
            documents = try await APIClient.shared.fetchDocuments()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func deleteDocument(_ document: DocumentItem) async {
        do {
            try await APIClient.shared.deleteDocument(id: document.documentID)
            documents.removeAll { $0.id == document.id }

            if selectedDocument?.id == document.id {
                selectedDocument = nil
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func uploadPDF(data: Data, filename: String) async {
        do {
            _ = try await APIClient.shared.uploadPDF(
                data: data,
                filename: filename
            )
            await loadDocuments()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

