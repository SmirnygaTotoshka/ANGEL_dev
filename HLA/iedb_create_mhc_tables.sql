#Скрипт iedb_create_mhc_tables.sql содержит описание первичной подготовки 
#таблиц для модели связывания MHC-epitope.

#Критерии фильтрации следующие:
#  - mhc_bind и mhc_elution
#    - Должен быть ИД публикации
#    - Должен быть ИД эпитопа
#    - Должен быть исход эксперимента
#    - Должен быть ИД аллеля MHC
#  - для эпитопов
#    - Должна быть линейная последовательность эпитопа
#    - Эта последовательность не должна содержать модификаций
#    - Должна быть последовательность белка-источника.
#  - для аллеля МНС
#    - аллель должен быть человеческий
#    - аллель должен быть первого класса МНС
#    - аллель должен быть записан в формате HLA-<ген>*<аллельная группа>:<белковый продукт>
USE iedb;
CREATE TABLE filtered_bind
AS (SELECT reference_id, curated_epitope_id, as_char_value,
as_location, category, assay_type,units,
as_num_value,as_inequality,as_comments, mhc_allele_restriction_id 
    FROM mhc_bind
    INNER JOIN assay_type ON as_type_id = assay_type_id
    WHERE reference_id IS NOT NULL AND
          curated_epitope_id IS NOT NULL AND
          as_char_value IS NOT NULL AND
          mhc_allele_restriction_id IS NOT NULL);
          
CREATE INDEX filtered_bind_index ON filtered_bind (curated_epitope_id,mhc_allele_restriction_id);

CREATE TABLE filtered_elution
AS (SELECT reference_id, curated_epitope_id, as_char_value, as_location, 
category, assay_type, as_num_value, as_inequality, units, 
as_num_subjects, as_num_responded, as_response_frequency, as_comments,
as_immunization_comments,h_sex, h_age, mhc_allele_restriction_id,
h_organism_id, ant_type, ant_ref_name, ant_object_id, apc_cell_type,
apc_tissue_type, apc_origin
    FROM mhc_elution
    INNER JOIN assay_type ON as_type_id = assay_type_id
    WHERE reference_id IS NOT NULL AND
          curated_epitope_id IS NOT NULL AND
          as_char_value IS NOT NULL AND
          mhc_allele_restriction_id IS NOT NULL);
          
CREATE INDEX filtered_elution_index ON filtered_elution (curated_epitope_id,mhc_allele_restriction_id);

CREATE TABLE filtered_epitope_cur
AS (SELECT curated_epitope_id, e_name, 
source_antigen_accession, description ,e_region_domain_flag,
e_ev, linear_peptide_seq, e_ref_start,
e_ref_end, `database`, name, sequence, organism_name
    FROM curated_epitope
    INNER JOIN epitope_object eo ON eo.object_id = e_object_id
    INNER JOIN epitope e ON e.epitope_id = eo.epitope_id
    INNER JOIN source s ON s.accession = source_antigen_accession
    WHERE linear_peptide_seq IS NOT NULL AND 
          linear_peptide_modification IS NULL AND
          sequence IS NOT NULL);
          
CREATE INDEX filtered_epitope_cur_index ON filtered_epitope_cur (curated_epitope_id);

#9606 - Taxonomy ID для Homo Sapiens
CREATE TABLE filtered_mhc
AS (SELECT mhc_allele_restriction_id, 
restriction_level,displayed_restriction, organism_ncbi_tax_id,class, chain_i_name
    FROM mhc_allele_restriction
    WHERE restriction_level = 'complete molecule' AND
          organism_ncbi_tax_id = 9606 AND
          class = 'I');
          
CREATE INDEX filtered_mhc_index ON filtered_mhc (mhc_allele_restriction_id);


CREATE TABLE epi_mhc_bind
AS (SELECT fb.curated_epitope_id, fb.mhc_allele_restriction_id, reference_id, as_char_value, as_location, 
category, assay_type,units,as_num_value,as_inequality,as_comments,
e_name, source_antigen_accession, description ,e_region_domain_flag, e_ev, linear_peptide_seq, 
e_ref_start,e_ref_end, `database`, name, sequence, organism_name, 
restriction_level,displayed_restriction, organism_ncbi_tax_id,class, chain_i_name
    FROM filtered_bind fb
    INNER JOIN filtered_mhc fm ON fm.mhc_allele_restriction_id = fb.mhc_allele_restriction_id
    INNER JOIN filtered_epitope_cur fe ON fe.curated_epitope_id = fb.curated_epitope_id);
    
CREATE INDEX epi_mhc_bind_index ON epi_mhc_bind (curated_epitope_id,mhc_allele_restriction_id);

CREATE TABLE epi_mhc_elution
AS (SELECT reference_id, fel.curated_epitope_id, as_char_value, as_location, 
category, assay_type, as_num_value, as_inequality, units, 
as_num_subjects, as_num_responded, as_response_frequency, as_comments,
as_immunization_comments,h_sex, h_age, fel.mhc_allele_restriction_id,
h_organism_id, ant_type, ant_ref_name, ant_object_id, apc_cell_type,
apc_tissue_type, apc_origin,
e_name, source_antigen_accession, description ,e_region_domain_flag, e_ev, linear_peptide_seq, e_ref_start,e_ref_end, `database`, name, sequence, organism_name, 
restriction_level,displayed_restriction, organism_ncbi_tax_id,class, chain_i_name
    FROM filtered_elution fel
    INNER JOIN filtered_mhc fm ON fm.mhc_allele_restriction_id = fel.mhc_allele_restriction_id
    INNER JOIN filtered_epitope_cur fe ON fe.curated_epitope_id = fel.curated_epitope_id);
    
CREATE INDEX epi_mhc_elution_index ON epi_mhc_elution (curated_epitope_id,mhc_allele_restriction_id);
