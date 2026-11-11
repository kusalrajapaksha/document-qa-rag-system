//
//  DocumentListView.swift
//  DocuMind-iOS
//
//  Created by Kusal on 2026-10-22.
//


import SwiftUI
import UniformTypeIdentifiers

struct DocumentListView: View {
    @StateObject private var viewModel = DocumentViewModel()
    @State private var showPDFPicker = false

    var body: some View {
        NavigationStack {
            VStack {
                Group {
                    if viewModel.isLoading && viewModel.documents.isEmpty {
                        ProgressView("Loading documents...")
                    } else if viewModel.documents.isEmpty {
                        ContentUnavailableView(
                            "No Documents",
                            systemImage: "doc.text",
                            description: Text("Upload a PDF to start asking questions.")
                        )
                    } else {
                        List {
                            ForEach(viewModel.documents) { document in
                                NavigationLink {
                                    AskDocumentView(document: document)
                                } label: {
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text(document.filename)
                                            .font(.headline)
                                            .lineLimit(2)

                                        Text("\(document.pageCount) pages · \(document.chunkCount) chunks")
                                            .font(.subheadline)
                                            .foregroundStyle(.secondary)

                                        Text(document.documentID)
                                            .font(.caption2)
                                            .foregroundStyle(.tertiary)
                                            .lineLimit(1)
                                    }
                                    .padding(.vertical, 4)
                                }
                                .swipeActions {
                                    Button(role: .destructive) {
                                        Task {
                                            await viewModel.deleteDocument(document)
                                        }
                                    } label: {
                                        Label("Delete", systemImage: "trash")
                                    }
                                }
                            }
                        }
                        .refreshable {
                            await viewModel.loadDocuments()
                        }
                    }
                    
                    HStack {
                        Image(.ollama)
                            .resizable()
                            .scaledToFit()
                            .frame(width: 24, height: 24)
                        
                        Text("Ollama Powered")
                            .fontWeight(.regular)
                            .foregroundStyle(.gray)
                    }
                   
                }
            }
            .navigationTitle("DocuMind")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showPDFPicker = true
                    } label: {
                        Image(systemName: "plus")
                    }
                    .accessibilityLabel("Upload PDF")
                }
                
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Task {
                            await viewModel.loadDocuments()
                        }
                    } label: {
                        Image(systemName: "arrow.down.to.line.compact")
                    }
                    .accessibilityLabel("Download PDF")
                }
            }
            .task {
                await viewModel.loadDocuments()
            }
            .fileImporter(
                isPresented: $showPDFPicker,
                allowedContentTypes: [.pdf],
                allowsMultipleSelection: false
            ) { result in
                Task {
                    await handlePDFSelection(result)
                }
            }
            .alert(
                "Something went wrong",
                isPresented: Binding(
                    get: { viewModel.errorMessage != nil },
                    set: { if !$0 { viewModel.errorMessage = nil } }
                )
            ) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(viewModel.errorMessage ?? "")
            }
        }
    }

    private func handlePDFSelection(
        _ result: Result<[URL], Error>
    ) async {
        do {
            guard let url = try result.get().first else { return }

            let hasAccess = url.startAccessingSecurityScopedResource()
            defer {
                if hasAccess {
                    url.stopAccessingSecurityScopedResource()
                }
            }

            let data = try Data(contentsOf: url)

            await viewModel.uploadPDF(
                data: data,
                filename: url.lastPathComponent
            )
        } catch {
            viewModel.errorMessage = error.localizedDescription
        }
    }
}
