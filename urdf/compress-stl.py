import os
import shutil
import open3d as o3d
from pathlib import Path
import argparse

def compress_stls(input_folder, reduction_factor=0.1):
    base_dir = Path(input_folder)
    output_dir = base_dir / "compressed"
    output_dir.mkdir(exist_ok=True)

    stl_files = list(base_dir.glob("*.[sS][tT][lL]"))
    
    if not stl_files:
        print(f"Aucun fichier STL trouvé dans {base_dir.absolute()}")
        return

    print(f"Début du traitement de {len(stl_files)} fichiers...")

    for file_path in stl_files:
        # 1. Charger le mesh
        mesh = o3d.io.read_triangle_mesh(str(file_path))
        original_triangles = len(mesh.triangles)
        
        if original_triangles == 0:
            print(f"  -> {file_path.name} est déjà vide à la source. Ignoré.")
            continue

        mesh.remove_duplicated_vertices()
        mesh.remove_duplicated_triangles()
        mesh.remove_degenerate_triangles()
        mesh.remove_unreferenced_vertices()

        target_triangles = max(50, int(original_triangles * reduction_factor))
        compressed_mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
        
        output_path = output_dir / file_path.name

        if len(compressed_mesh.triangles) == 0:
            print(f"  [!] Échec sur {file_path.name} (Géométrie complexe). Copie de l'original.")
            shutil.copy(str(file_path), str(output_path))
        else:
            compressed_mesh.compute_vertex_normals()
            o3d.io.write_triangle_mesh(str(output_path), compressed_mesh, write_ascii=False)
            print(f"  [OK] {file_path.name} : {original_triangles} -> {len(compressed_mesh.triangles)} faces")


def list_stls(input_folder):
    base_dir = Path(input_folder)
    stl_files = list(base_dir.glob("*.[sS][tT][lL]"))

    if not stl_files:
        print(f"Aucun fichier STL trouvé dans {base_dir.absolute()}")
        return

    print(f"Liste des fichiers STL dans {base_dir.absolute()} :")
    for file_path in stl_files:
        mesh = o3d.io.read_triangle_mesh(str(file_path))
        print(f"  - {file_path.name} : {len(mesh.triangles)} triangles")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compresser ou lister des fichiers STL")
    parser.add_argument("--input", default="../meshes/", help="Dossier contenant les fichiers STL")
    parser.add_argument("--reduction-factor", type=float, default=0.1, help="Facteur de réduction pour la compression")
    parser.add_argument("--list", action="store_true", help="Lister les fichiers STL et leur nombre de triangles")
    args = parser.parse_args()

    if args.list:
        list_stls(args.input)
    else:
        compress_stls(args.input, reduction_factor=args.reduction_factor)
        print("\nOpération terminée !")