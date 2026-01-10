import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import {
  Upload,
  FileSpreadsheet,
  ArrowRight,
  AlertTriangle,
  Check,
  X,
  RefreshCw,
  Save,
  ChevronDown,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// CRM fields that can be mapped
const CRM_FIELDS = [
  { value: "empresa", label: "Empresa", required: true },
  { value: "contacto", label: "Contacto", required: false },
  { value: "email", label: "Email", required: true },
  { value: "telefono", label: "Teléfono", required: false },
  { value: "cargo", label: "Cargo", required: false },
  { value: "sector", label: "Sector", required: false },
  { value: "valor_estimado", label: "Valor EUR", required: false },
  { value: "etapa", label: "Etapa", required: false },
  { value: "fuente", label: "Fuente", required: false },
  { value: "notas", label: "Notas", required: false },
];

export default function ImportModal({ open, onClose, onSuccess }) {
  const [step, setStep] = useState(1); // 1: Upload, 2: Map columns, 3: Review duplicates
  const [file, setFile] = useState(null);
  const [fileData, setFileData] = useState({ headers: [], rows: [], preview: [] });
  const [columnMapping, setColumnMapping] = useState({});
  const [savedMappings, setSavedMappings] = useState([]);
  const [duplicates, setDuplicates] = useState([]);
  const [duplicateActions, setDuplicateActions] = useState({});
  const [loading, setLoading] = useState(false);
  const [parseLoading, setParseLoading] = useState(false);

  // Load saved mappings on mount
  useEffect(() => {
    const saved = localStorage.getItem("crm_import_mappings");
    if (saved) {
      try {
        setSavedMappings(JSON.parse(saved));
      } catch (e) {
        console.error("Error loading saved mappings:", e);
      }
    }
  }, []);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setStep(1);
      setFile(null);
      setFileData({ headers: [], rows: [], preview: [] });
      setColumnMapping({});
      setDuplicates([]);
      setDuplicateActions({});
    }
  }, [open]);

  // Check if required fields are mapped
  const requiredFieldsMapped = useMemo(() => {
    const mappedFields = Object.values(columnMapping);
    return CRM_FIELDS
      .filter((f) => f.required)
      .every((f) => mappedFields.includes(f.value));
  }, [columnMapping]);

  // Handle file selection
  const handleFileSelect = async (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setParseLoading(true);

    // Send file to backend for parsing
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(`${API}/leads/parse`, formData, {
        withCredentials: true,
        headers: { "Content-Type": "multipart/form-data" },
      });

      const { headers, rows, preview } = response.data;
      setFileData({ headers, rows, preview });

      // Auto-detect column mapping
      const autoMapping = {};
      headers.forEach((header, index) => {
        const normalizedHeader = header.toLowerCase().trim();
        CRM_FIELDS.forEach((field) => {
          const fieldAliases = {
            empresa: ["empresa", "company", "compañía", "compania", "organizacion", "organización"],
            contacto: ["contacto", "contact", "nombre", "name", "persona"],
            email: ["email", "correo", "e-mail", "mail"],
            telefono: ["telefono", "teléfono", "phone", "tel", "móvil", "movil"],
            cargo: ["cargo", "position", "puesto", "título", "titulo", "job"],
            sector: ["sector", "industry", "industria", "rubro"],
            valor_estimado: ["valor", "value", "monto", "amount", "precio", "eur", "valor_eur"],
            etapa: ["etapa", "stage", "estado", "status", "fase"],
            fuente: ["fuente", "source", "origen", "canal"],
            notas: ["notas", "notes", "comentarios", "comments", "observaciones"],
          };

          const aliases = fieldAliases[field.value] || [field.value];
          if (aliases.some((alias) => normalizedHeader.includes(alias))) {
            if (!autoMapping[index]) {
              autoMapping[index] = field.value;
            }
          }
        });
      });

      setColumnMapping(autoMapping);
      setStep(2);
    } catch (error) {
      toast.error("Error al procesar el archivo");
      console.error("Parse error:", error);
    } finally {
      setParseLoading(false);
    }
  };

  // Handle column mapping change
  const handleMappingChange = (columnIndex, crmField) => {
    setColumnMapping((prev) => {
      const newMapping = { ...prev };
      // Remove previous mapping for this field
      Object.keys(newMapping).forEach((key) => {
        if (newMapping[key] === crmField && key !== columnIndex.toString()) {
          delete newMapping[key];
        }
      });
      if (crmField === "none") {
        delete newMapping[columnIndex];
      } else {
        newMapping[columnIndex] = crmField;
      }
      return newMapping;
    });
  };

  // Save current mapping
  const saveMapping = () => {
    const mappingName = prompt("Nombre para este mapeo:");
    if (!mappingName) return;

    const newMapping = {
      id: Date.now(),
      name: mappingName,
      mapping: columnMapping,
      headers: fileData.headers,
    };

    const updated = [...savedMappings, newMapping];
    setSavedMappings(updated);
    localStorage.setItem("crm_import_mappings", JSON.stringify(updated));
    toast.success("Mapeo guardado");
  };

  // Load saved mapping
  const loadMapping = (savedMapping) => {
    // Match headers from saved mapping to current file
    const newMapping = {};
    fileData.headers.forEach((header, index) => {
      const savedIndex = savedMapping.headers.findIndex(
        (h) => h.toLowerCase().trim() === header.toLowerCase().trim()
      );
      if (savedIndex !== -1 && savedMapping.mapping[savedIndex]) {
        newMapping[index] = savedMapping.mapping[savedIndex];
      }
    });
    setColumnMapping(newMapping);
    toast.success("Mapeo cargado");
  };

  // Check for duplicates
  const checkDuplicates = async () => {
    setLoading(true);

    try {
      // Build data to check
      const dataToCheck = fileData.rows.map((row) => {
        const mapped = {};
        Object.entries(columnMapping).forEach(([colIndex, field]) => {
          mapped[field] = row[parseInt(colIndex)] || "";
        });
        return mapped;
      });

      const response = await axios.post(
        `${API}/leads/check-duplicates`,
        { leads: dataToCheck },
        { withCredentials: true }
      );

      const duplicatesFound = response.data.duplicates || [];
      setDuplicates(duplicatesFound);

      // Initialize actions for duplicates
      const actions = {};
      duplicatesFound.forEach((dup, index) => {
        actions[index] = "skip"; // Default action
      });
      setDuplicateActions(actions);

      setStep(3);
    } catch (error) {
      toast.error("Error al verificar duplicados");
      console.error("Duplicate check error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Import leads
  const handleImport = async () => {
    setLoading(true);

    try {
      // Build final data with actions
      const dataToImport = fileData.rows.map((row, index) => {
        const mapped = {};
        Object.entries(columnMapping).forEach(([colIndex, field]) => {
          mapped[field] = row[parseInt(colIndex)] || "";
        });

        // Find if this row is a duplicate
        const duplicateEntry = duplicates.find((d) => d.rowIndex === index);
        if (duplicateEntry) {
          mapped._action = duplicateActions[duplicates.indexOf(duplicateEntry)];
          mapped._existingId = duplicateEntry.existingLead?.lead_id;
        } else {
          mapped._action = "import";
        }

        return mapped;
      });

      const response = await axios.post(
        `${API}/leads/import-mapped`,
        { leads: dataToImport, mapping: columnMapping },
        { withCredentials: true }
      );

      toast.success(
        `${response.data.imported} leads importados, ${response.data.updated} actualizados, ${response.data.skipped} omitidos`
      );
      onSuccess?.();
      onClose();
    } catch (error) {
      toast.error("Error al importar leads");
      console.error("Import error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Get available fields for mapping (not yet mapped)
  const getAvailableFields = (currentColumn) => {
    const mappedFields = Object.entries(columnMapping)
      .filter(([col]) => col !== currentColumn.toString())
      .map(([, field]) => field);

    return CRM_FIELDS.filter(
      (f) => !mappedFields.includes(f.value) || columnMapping[currentColumn] === f.value
    );
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-slate-900 border-white/10 max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
            Importar Leads
            {step > 1 && (
              <Badge variant="outline" className="ml-2 border-cyan-400 text-cyan-400">
                Paso {step} de 3
              </Badge>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto">
          {/* Step 1: File Upload */}
          {step === 1 && (
            <div className="py-8">
              <div
                className="border-2 border-dashed border-slate-700 rounded-xl p-12 text-center hover:border-cyan-400 transition-colors cursor-pointer"
                onClick={() => document.getElementById("import-file-modal")?.click()}
              >
                <input
                  type="file"
                  id="import-file-modal"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                {parseLoading ? (
                  <div className="animate-pulse">
                    <RefreshCw className="w-12 h-12 mx-auto mb-4 text-cyan-400 animate-spin" />
                    <p className="text-slate-300">Procesando archivo...</p>
                  </div>
                ) : (
                  <>
                    <Upload className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                    <p className="text-lg font-medium text-slate-300 mb-2">
                      Arrastra un archivo o haz clic para seleccionar
                    </p>
                    <p className="text-sm text-slate-500">
                      Formatos soportados: CSV, Excel (.xlsx, .xls)
                    </p>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Column Mapping */}
          {step === 2 && (
            <div className="space-y-6">
              {/* File info */}
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
                  <span className="text-slate-300">{file?.name}</span>
                  <Badge variant="outline" className="border-slate-600">
                    {fileData.rows.length} filas
                  </Badge>
                </div>
                {savedMappings.length > 0 && (
                  <Select onValueChange={(v) => loadMapping(savedMappings.find((m) => m.id.toString() === v))}>
                    <SelectTrigger className="w-48 bg-slate-800 border-slate-700">
                      <SelectValue placeholder="Cargar mapeo guardado" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800">
                      {savedMappings.map((m) => (
                        <SelectItem key={m.id} value={m.id.toString()}>
                          {m.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              {/* Preview table */}
              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <div className="bg-slate-800/50 px-4 py-2 text-sm font-medium text-slate-400">
                  Vista previa (primeras 3 filas)
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-800">
                        {fileData.headers.map((header, index) => (
                          <th key={index} className="px-4 py-3 text-left">
                            <div className="space-y-2">
                              <div className="font-medium text-slate-300">{header}</div>
                              <Select
                                value={columnMapping[index] || "none"}
                                onValueChange={(v) => handleMappingChange(index, v)}
                              >
                                <SelectTrigger className="h-8 text-xs bg-slate-800 border-slate-700">
                                  <SelectValue placeholder="No mapear" />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-900 border-slate-800">
                                  <SelectItem value="none">No mapear</SelectItem>
                                  {getAvailableFields(index).map((field) => (
                                    <SelectItem key={field.value} value={field.value}>
                                      {field.label}
                                      {field.required && " *"}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {fileData.preview.map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-b border-slate-800/50">
                          {row.map((cell, cellIndex) => (
                            <td
                              key={cellIndex}
                              className={`px-4 py-2 text-slate-400 truncate max-w-[200px] ${
                                columnMapping[cellIndex] ? "text-slate-200" : ""
                              }`}
                            >
                              {cell || "-"}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Required fields info */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-400">Campos obligatorios:</span>
                  {CRM_FIELDS.filter((f) => f.required).map((field) => {
                    const isMapped = Object.values(columnMapping).includes(field.value);
                    return (
                      <Badge
                        key={field.value}
                        className={
                          isMapped
                            ? "bg-green-500/20 text-green-400 border-green-500/30"
                            : "bg-red-500/20 text-red-400 border-red-500/30"
                        }
                      >
                        {isMapped ? <Check className="w-3 h-3 mr-1" /> : <X className="w-3 h-3 mr-1" />}
                        {field.label}
                      </Badge>
                    );
                  })}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={saveMapping}
                  className="text-slate-400 hover:text-cyan-400"
                >
                  <Save className="w-4 h-4 mr-1" />
                  Guardar mapeo
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Duplicate Review */}
          {step === 3 && (
            <div className="space-y-4">
              {duplicates.length === 0 ? (
                <div className="text-center py-8">
                  <Check className="w-12 h-12 mx-auto mb-4 text-green-400" />
                  <h3 className="text-lg font-medium text-slate-300 mb-2">
                    No se encontraron duplicados
                  </h3>
                  <p className="text-slate-500">
                    Todos los {fileData.rows.length} leads están listos para importar.
                  </p>
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-2 p-3 bg-amber-500/10 rounded-lg border border-amber-500/30">
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                    <span className="text-amber-300">
                      Se encontraron {duplicates.length} posibles duplicados
                    </span>
                  </div>

                  <div className="space-y-3 max-h-[400px] overflow-y-auto">
                    {duplicates.map((dup, index) => (
                      <div
                        key={index}
                        className="p-4 rounded-lg border border-slate-800 bg-slate-800/30"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge
                                className={
                                  dup.type === "exact"
                                    ? "bg-red-500/20 text-red-400"
                                    : "bg-amber-500/20 text-amber-400"
                                }
                              >
                                {dup.type === "exact" ? "Duplicado exacto" : "Posible duplicado"}
                              </Badge>
                              <span className="text-xs text-slate-500">Fila {dup.rowIndex + 2}</span>
                            </div>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <div className="text-xs text-slate-500 mb-1">Nuevo (archivo)</div>
                                <div className="text-slate-300">{dup.newLead.empresa}</div>
                                <div className="text-slate-400">{dup.newLead.email}</div>
                                <div className="text-slate-400">{dup.newLead.contacto}</div>
                              </div>
                              <div>
                                <div className="text-xs text-slate-500 mb-1">Existente (CRM)</div>
                                <div className="text-slate-300">{dup.existingLead.empresa}</div>
                                <div className="text-slate-400">{dup.existingLead.email}</div>
                                <div className="text-slate-400">{dup.existingLead.contacto}</div>
                              </div>
                            </div>
                          </div>

                          <Select
                            value={duplicateActions[index]}
                            onValueChange={(v) =>
                              setDuplicateActions((prev) => ({ ...prev, [index]: v }))
                            }
                          >
                            <SelectTrigger className="w-40 bg-slate-800 border-slate-700">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-slate-900 border-slate-800">
                              <SelectItem value="skip">Omitir</SelectItem>
                              <SelectItem value="import">Importar igual</SelectItem>
                              <SelectItem value="update">Actualizar existente</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <DialogFooter className="border-t border-slate-800 pt-4">
          <div className="flex justify-between w-full">
            <div>
              {step > 1 && (
                <Button
                  variant="ghost"
                  onClick={() => setStep(step - 1)}
                  className="text-slate-400"
                >
                  Atrás
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={onClose}
                className="border-white/10 text-slate-300 hover:bg-slate-800"
              >
                Cancelar
              </Button>

              {step === 2 && (
                <Button
                  onClick={checkDuplicates}
                  disabled={!requiredFieldsMapped || loading}
                  className="btn-gradient"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <ArrowRight className="w-4 h-4 mr-2" />
                  )}
                  Verificar duplicados
                </Button>
              )}

              {step === 3 && (
                <Button onClick={handleImport} disabled={loading} className="btn-gradient">
                  {loading ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4 mr-2" />
                  )}
                  Importar {fileData.rows.length - duplicates.filter((_, i) => duplicateActions[i] === "skip").length} leads
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
