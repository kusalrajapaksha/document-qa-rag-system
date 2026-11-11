//
//  AskDocumentView.swift
//  DocuMind-iOS
//
//  Created by Kusal on 2026-10-22.
//


import SwiftUI

struct AskDocumentView: View {
    let document: DocumentItem

    @State private var question = ""
    @State private var response: AskDocumentResponse?
    @State private var isAsking = false
    @State private var errorMessage: String?

    var body: some View {
        List {
            Section("Ask a question") {
                TextField("What does this document say?", text: $question)
                    .accessibilityIdentifier("questionField")

                Button {
                    Task {
                        await askQuestion()
                    }
                } label: {
                    HStack {
                        Spacer()
                        if isAsking {
                            ProgressView()
                        } else {
                            Label("Ask", systemImage: "sparkles")
                        }
                        Spacer()
                    }
                }
                .disabled(question.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isAsking)
            }

            if let response {
                Section("Answer") {
                    Text(response.answer)
                        .textSelection(.enabled)
                }

                Section("Sources") {
                    ForEach(response.sources) { source in
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Page \(source.pageNumber)")
                                .font(.headline)

                            Text(source.text)
                                .font(.body)
                                .textSelection(.enabled)

                            Text("Similarity: \(source.similarityScore, specifier: "%.2f")")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
        }
        .navigationTitle("Ask Document")
        .navigationBarTitleDisplayMode(.inline)
        .alert(
            "Something went wrong",
            isPresented: Binding(
                get: { errorMessage != nil },
                set: { if !$0 { errorMessage = nil } }
            )
        ) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage ?? "")
        }
    }

    private func askQuestion() async {
        isAsking = true
        defer { isAsking = false }

        do {
            response = try await APIClient.shared.ask(
                question: question,
                documentID: document.documentID
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
