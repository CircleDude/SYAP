def cpp_to_python(cpp_code: str) -> str:
    lines = cpp_code.strip().split("\n")
    indent = 0
    result = []

    for raw_line in lines:
        original_line = raw_line
        line = raw_line.strip()

        if not line or line.startswith("#include"):
            continue

        # Фигурные скобки
        if line.endswith("{"):
            line = line[:-1].strip()

        if line.startswith("}"):
            indent = max(indent - 1, 0)
            line = line[1:].strip()

        # Убираем ;
        if line.endswith(";"):
            line = line[:-1].strip()

        # Перевод &(ar[l1]) -> ar[l1:]
        if "&(" in line:
            line = line.replace("&(", "").replace(")", "") + ":"  # ar[l1]:

        # Убираем типы только в начале строки
        type_keywords = ["int ", "unsigned int ", "int*", "int *"]
        for t in type_keywords:
            if line.startswith(t):
                line = line[len(t):].strip()

        # ++ и --
        line = line.replace("++", " += 1").replace("--", " -= 1")

        # Логические операторы
        line = line.replace("&&", "and").replace("||", "or")

        # Перевод new int[n]
        if "new int[" in line:
            left, right = line.split("=", 1)
            left = left.strip()
            right = right.strip()

            if "{" in right:
                # Инициализация: new int[n]{1,2,3}
                values = right[right.find("{") + 1:right.find("}")]
                line = f"{left} = [{values}]"
            else:
                size = right[right.find("[") + 1:right.find("]")]
                line = f"{left} = [0] * {size}"

        # Функции
        if line.startswith("int ") or line.startswith("int*"):
            # Не даём испортить строки вида int n = 10;
            pass

        if "(" in line and ")" in line and \
           not line.startswith(("if", "while", "for", "else", "return")) \
           and "=" not in line \
           and not line.endswith(":"):
            name = line.split("(")[0].split()[-1]
            args = line[line.find("(")+1:line.find(")")]
            args = ", ".join(a.strip().split()[-1].replace("*", "") for a in args.split(",") if a.strip())
            result.append(" " * (4 * indent) + f"def {name}({args}):")
            indent += 1
            continue

        # if
        if line.startswith("if"):
            cond = line[line.find("(")+1:line.rfind(")")]
            result.append(" " * (4 * indent) + f"if {cond}:")
            indent += 1
            continue

        # else
        if line.startswith("else"):
            indent -= 1
            result.append(" " * (4 * indent) + "else:")
            indent += 1
            continue

        # while
        if line.startswith("while"):
            cond = line[line.find("(")+1:line.rfind(")")]
            result.append(" " * (4 * indent) + f"while {cond}:")
            indent += 1
            continue

        # for
        if line.startswith("for"):
            inside = line[line.find("(")+1:line.find(")")]
            init, cond, step = [p.strip() for p in inside.split(";")]

            var = init.split("=")[0].strip().split()[-1]
            start = init.split("=")[1].strip()

            end = cond.split("<")[-1].strip()

            if "++" in step:
                step_val = "1"
            elif "--" in step:
                step_val = "-1"
            elif "+=" in step:
                step_val = step.split("=")[1].strip()
            elif "-=" in step:
                step_val = "-" + step.split("=")[1].strip()
            else:
                step_val = "1"

            result.append(" " * (4 * indent) +
                          f"for {var} in range({start}, {end}, {step_val}):")
            indent += 1
            continue

        # std::cout
        if "std::cout" in line:
            # Преобразуем: std::cout << m[i] << ' ';
            tokens = line.split("<<")
            python_parts = []
            for t in tokens[1:]:
                t = t.strip()
                if t == "' '":
                    python_parts.append("' '")
                else:
                    python_parts.append(t)
            line = "print(" + ", ".join(python_parts) + ", end='')"

        # main()
        if line.startswith("int main"):
            result.append("def main():")
            indent += 1
            continue

        # Обычная строка
        if line:
            result.append(" " * (4 * indent) + line)

    return "\n".join(result)



cpp_code = """\
#include <iostream>

int* Merge(int *ar1,const unsigned int l1,int *ar2,const unsigned int l2) {
	int *ar;
	unsigned int n = l1+l2;
	int i,j;

	ar = new int[n];
	i = j = 0;
	while (i+j < n) {
		if ((j>=l2) or ((i<l1) and (ar1[i]<ar2[j]))) {
			ar[i+j] = (ar1[i]);
			++i;
		}
		else {
			ar[i+j] = (ar2[j]);
			++j;
		}
	}
	return ar;
}
int* MergeSortRec(int *ar,const unsigned int n) {
	if (n > 1) {
		unsigned int l1 = n/2;
		unsigned int l2 = n-l1;

		return Merge(MergeSortRec(ar,l1),l1,MergeSortRec(&(ar[l1]),l2),l2);
	}
	return ar;
}

int main() {
  int n = 10;
  int* m = new int[n]{4,7,3,1,8,6,4,2,4,0};
  int* m_;
  
  m_ = MergeSortRec(m,10);
  
  for (int i=0; i<n; i++) std::cout << m_[i] << ' ';
}
"""

print(cpp_to_python(cpp_code))
