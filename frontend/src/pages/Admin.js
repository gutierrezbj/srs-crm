import { useState, useEffect } from "react";
import axios from "axios";
import { 
  Users, 
  Plus, 
  Edit2, 
  Trash2,
  Shield,
  User,
  Mail,
  AlertTriangle,
  Database
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Admin({ user }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({ email: "", name: "", role: "user" });
  const [deleteAllDialogOpen, setDeleteAllDialogOpen] = useState(false);
  const [confirmDeleteText, setConfirmDeleteText] = useState("");
  const [leadCount, setLeadCount] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`, { withCredentials: true });
      setUsers(response.data);
    } catch (error) {
      toast.error("Error al cargar usuarios");
    } finally {
      setLoading(false);
    }
  };

  const openModal = (userToEdit = null) => {
    if (userToEdit) {
      setEditingUser(userToEdit);
      setFormData({
        email: userToEdit.email,
        name: userToEdit.name,
        role: userToEdit.role,
      });
    } else {
      setEditingUser(null);
      setFormData({ email: "", name: "", role: "user" });
    }
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingUser(null);
    setFormData({ email: "", name: "", role: "user" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingUser) {
        await axios.put(
          `${API}/users/${editingUser.user_id}`,
          { name: formData.name, role: formData.role },
          { withCredentials: true }
        );
        toast.success("Usuario actualizado");
      } else {
        await axios.post(`${API}/users`, formData, { withCredentials: true });
        toast.success("Usuario creado");
      }
      closeModal();
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al guardar usuario");
    }
  };

  const handleDelete = async (userId, userName) => {
    if (!window.confirm(`¿Eliminar a ${userName}?`)) return;
    
    try {
      await axios.delete(`${API}/users/${userId}`, { withCredentials: true });
      toast.success("Usuario eliminado");
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al eliminar usuario");
    }
  };

  if (user?.role !== "admin") {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="w-12 h-12 mx-auto mb-4 text-red-400 opacity-50" />
          <h2 className="text-xl font-semibold theme-text mb-2">Acceso Denegado</h2>
          <p className="theme-text-secondary">Solo administradores pueden acceder a esta sección.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-cyan-400 animate-pulse">Cargando usuarios...</div>
      </div>
    );
  }

  return (
    <div data-testid="admin-page" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold theme-text flex items-center gap-2">
            <Shield className="w-6 h-6 text-cyan-400" />
            Administración
          </h1>
          <p className="theme-text-secondary text-sm">Gestión de usuarios del CRM</p>
        </div>
        <Button
          onClick={() => openModal()}
          data-testid="new-user-btn"
          className="btn-gradient"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Users List */}
      <Card className="theme-bg-secondary border theme-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold theme-text flex items-center gap-2">
            <Users className="w-5 h-5" />
            Usuarios ({users.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {users.length === 0 ? (
            <div className="text-center py-8 theme-text-muted">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No hay usuarios registrados</p>
            </div>
          ) : (
            <div className="space-y-3">
              {users.map((u) => (
                <div
                  key={u.user_id}
                  className="flex items-center justify-between p-4 rounded-lg theme-bg-tertiary border theme-border"
                  data-testid={`user-row-${u.user_id}`}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-semibold">
                      {u.name?.charAt(0) || "U"}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium theme-text">{u.name}</span>
                        <Badge className={u.role === "admin" ? "bg-cyan-500 text-white" : "bg-slate-600 text-white"}>
                          {u.role === "admin" ? "Admin" : "Usuario"}
                        </Badge>
                        {u.user_id === user.user_id && (
                          <Badge variant="outline" className="border-cyan-400 text-cyan-400">
                            Tú
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm theme-text-secondary flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        {u.email}
                      </p>
                    </div>
                  </div>
                  
                  {u.user_id !== user.user_id && (
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openModal(u)}
                        className="theme-text-secondary hover:text-cyan-400"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(u.user_id, u.name)}
                        className="theme-text-secondary hover:text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Modal */}
      <Dialog open={modalOpen} onOpenChange={closeModal}>
        <DialogContent className="bg-slate-900 border-white/10">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold text-white flex items-center gap-2">
              <User className="w-5 h-5 text-cyan-400" />
              {editingUser ? "Editar Usuario" : "Nuevo Usuario"}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label className="text-slate-300 flex items-center gap-2">
                <Mail className="w-4 h-4" />
                Email
              </Label>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                required
                disabled={!!editingUser}
                data-testid="user-email"
                className="bg-slate-950 border-slate-800 focus:border-cyan-400 disabled:opacity-50"
                placeholder="usuario@systemrapidsolutions.com"
              />
              {!editingUser && (
                <p className="text-xs text-slate-500">
                  El usuario podrá acceder con este email de Google
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300 flex items-center gap-2">
                <User className="w-4 h-4" />
                Nombre
              </Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                required
                data-testid="user-name"
                className="bg-slate-950 border-slate-800 focus:border-cyan-400"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300 flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Rol
              </Label>
              <Select
                value={formData.role}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, role: value }))}
              >
                <SelectTrigger className="bg-slate-950 border-slate-800" data-testid="user-role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800">
                  <SelectItem value="user">Usuario</SelectItem>
                  <SelectItem value="admin">Administrador</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-slate-500">
                Los administradores pueden gestionar usuarios y configuración
              </p>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={closeModal}
                className="border-white/10 text-slate-300 hover:bg-slate-800"
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                data-testid="user-submit"
                className="btn-gradient"
              >
                {editingUser ? "Guardar Cambios" : "Crear Usuario"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
