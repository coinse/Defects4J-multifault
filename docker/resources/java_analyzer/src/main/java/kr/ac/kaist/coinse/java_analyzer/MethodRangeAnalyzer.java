package kr.ac.kaist.coinse.java_analyzer;

import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.utils.CodeGenerationUtils;
import com.github.javaparser.utils.Log;
import com.github.javaparser.utils.SourceRoot;

import java.util.List;
import java.util.LinkedList;
import java.nio.file.Paths;

/**
 * Some code that uses JavaParser.
 */
public class MethodRangeAnalyzer {
    public static void main(String[] args) {
        // JavaParser has a minimal logging class that normally logs nothing.
        // Let's ask it to write to standard out:
        Log.setAdapter(new Log.StandardOutStandardErrorAdapter());

        // /tmp/Closure-12b/src/com/google/javascript/jscomp/Normalize.java

        //SourceRoot sourceRoot = new SourceRoot(Paths.get("/tmp/Closure-12b/src/com/google/javascript/jscomp/"));
        //CompilationUnit cu = sourceRoot.parse("", "Normalize.java");

        SourceRoot sourceRoot = new SourceRoot(Paths.get(args[0]));
        CompilationUnit cu = sourceRoot.parse("", args[1]);

        cu.accept(new VoidVisitorAdapter<Void>() {
            @Override
            public void visit(MethodDeclaration n, Void arg) {
                super.visit(n, arg);
                int beginLine, endLine;
                if (n.getRange().isPresent()) {
                    Range range = n.getRange().get();
                    beginLine = range.begin.line;
                    endLine = range.end.line;
                }
                else {
                    beginLine = -1;
                    endLine = -1;
                }
                System.out.println("[method]|" + n.getSignature() + "|" + beginLine + "|" + endLine);
            }
            @Override
            public void visit(ConstructorDeclaration n, Void arg) {
                super.visit(n, arg);
                int beginLine, endLine;
                if (n.getRange().isPresent()) {
                    Range range = n.getRange().get();
                    beginLine = range.begin.line;
                    endLine = range.end.line;
                }
                else {
                    beginLine = -1;
                    endLine = -1;
                }
                System.out.println("[constructor]|" + n.getSignature() + "|" + beginLine + "|" + endLine);
            }
            @Override
            public void visit(FieldDeclaration n, Void arg) {
                super.visit(n, arg);
                int beginLine, endLine;
                if (n.getRange().isPresent()) {
                    Range range = n.getRange().get();
                    beginLine = range.begin.line;
                    endLine = range.end.line;
                }
                else {
                    beginLine = -1;
                    endLine = -1;
                }
                List<String> varNames = new LinkedList<>();
                for (VariableDeclarator var: n.getVariables()) {
                    varNames.add(var.getName().toString());
                }
                System.out.println("[field]|" + String.join(",", varNames) + "|" + beginLine + "|" + endLine);
            }

        }, null);
    }

}
