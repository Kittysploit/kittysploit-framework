from kittysploit.core.base.io import print_error, print_table

def syscall(arch, syscall_function) -> None:
    """
    Found syscall function
    :param arch: architecture
    :param syscall_function: syscall function
    """
    if arch == "x86":
        syscall_file = "data/syscall/intel_x86.csv"
    
    elif arch == "x64":
        syscall_file = "data/syscall/intel_x86_64.csv"
    
    elif arch == "arm":
        syscall_file = "data/syscall/arm32.csv"
    
    elif arch == "arm64":
        syscall_file = "data/syscall/arm64.csv"
    
    else:
        print_error("Invalid architecture")
        print_error("Supported architectures: x32, x64")
        return None

    headers = ["Syscall Number", "Syscall Name", "Hex Value", "Param 1", "Param 2", "Param 3", "Param 4", "Param 5", "Source File"]
    result = []

    with open(syscall_file, "r") as f:
        for line in f.readlines():
            row = line.strip().split(",")
            for element in row:
                if syscall_function in element:
                    result.append(row)
                    break

    print_table(headers, *result, highlight={syscall_function: "red"})