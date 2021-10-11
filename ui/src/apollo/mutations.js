import gql from "graphql-tag";

const ADD_PROJECT = gql`
  mutation addProject(
    $ecosystemId: ID
    $name: String
    $title: String
    $parentId: ID
  ) {
    addProject(
      ecosystemId: $ecosystemId
      name: $name
      title: $title
      parentId: $parentId
    ) {
      project {
        id
        name
      }
    }
  }
`;

const DELETE_PROJECT = gql`
  mutation deleteProject($id: ID) {
    deleteProject(id: $id) {
      project {
        id
      }
    }
  }
`;

const MOVE_PROJECT = gql`
  mutation moveProject($fromProjectId: ID, $toProjectId: ID) {
    moveProject(fromProjectId: $fromProjectId, toProjectId: $toProjectId) {
      project {
        id
        name
      }
    }
  }
`;

const UPDATE_PROJECT = gql`
  mutation updateProject($data: ProjectInputType, $id: ID) {
    updateProject(data: $data, id: $id) {
      project {
        id
        name
      }
    }
  }
`;

const ADD_ECOSYSTEM = gql`
  mutation addEcosystem($name: String!, $title: String, $description: String) {
    addEcosystem(name: $name, title: $title, description: $description) {
      ecosystem {
        id
      }
    }
  }
`;

const UPDATE_ECOSYSTEM = gql`
  mutation updateEcosystem($data: EcosystemInputType, $id: ID) {
    updateEcosystem(data: $data, id: $id) {
      ecosystem {
        id
      }
    }
  }
`;

const DELETE_ECOSYSTEM = gql`
  mutation deleteEcosystem($id: ID!) {
    deleteEcosystem(id: $id) {
      ecosystem {
        id
      }
    }
  }
`;

const TOKEN_AUTH = gql`
  mutation tokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      token
    }
  }
`;

const ADD_DATASET = gql`
  mutation addDataset(
    $category: String
    $datasourceName: String
    $filters: JSONString
    $projectId: ID!
    $uri: String
  ) {
    addDataset(
      category: $category
      datasourceName: $datasourceName
      filters: $filters
      projectId: $projectId
      uri: $uri
    ) {
      dataset {
        id
        datasource {
          uri
        }
      }
    }
  }
`;

const DELETE_DATASET = gql`
  mutation deleteDataset($id: ID!) {
    deleteDataset(id: $id) {
      dataset {
        id
      }
    }
  }
`;

const ARCHIVE_DATASET = gql`
  mutation archiveDataset($id: ID!) {
    archiveDataset(id: $id) {
      dataset {
        id
        isArchived
      }
    }
  }
`;

const UNARCHIVE_DATASET = gql`
  mutation unarchiveDataset($id: ID!) {
    unarchiveDataset(id: $id) {
      dataset {
        id
        isArchived
      }
    }
  }
`;

const FETCH_GITHUB_OWNER_REPOS = gql`
  mutation fetchGithubOwnerRepos($owner: String!) {
    fetchGithubOwnerRepos(owner: $owner) {
      jobId
    }
  }
`;

const ADD_CREDENTIAL = gql`
  mutation addCredential(
    $datasourceName: String!
    $token: String!
    $name: String!
  ) {
    addCredential(datasourceName: $datasourceName, token: $token, name: $name) {
      credential {
        id
      }
    }
  }
`;

const DELETE_CREDENTIAL = gql`
  mutation deleteCredential($id: ID!) {
    deleteCredential(id: $id) {
      credential {
        id
      }
    }
  }
`;

const addProject = (apollo, data) => {
  const response = apollo.mutate({
    mutation: ADD_PROJECT,
    variables: {
      ecosystemId: data.ecosystemId,
      name: data.name,
      title: data.title,
      parentId: data.parentId
    }
  });
  return response;
};

const deleteProject = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_PROJECT,
    variables: {
      id: id
    }
  });
  return response;
};

const moveProject = (apollo, fromProjectId, toProjectId) => {
  const response = apollo.mutate({
    mutation: MOVE_PROJECT,
    variables: {
      fromProjectId: fromProjectId,
      toProjectId: toProjectId
    }
  });
  return response;
};

const updateProject = (apollo, data, id) => {
  const response = apollo.mutate({
    mutation: UPDATE_PROJECT,
    variables: {
      data: data,
      id: id
    }
  });
  return response;
};

const addEcosystem = (apollo, data) => {
  const response = apollo.mutate({
    mutation: ADD_ECOSYSTEM,
    variables: {
      name: data.name,
      title: data.title,
      description: data.description
    }
  });
  return response;
};

const updateEcosystem = (apollo, data, id) => {
  const response = apollo.mutate({
    mutation: UPDATE_ECOSYSTEM,
    variables: {
      data: data,
      id: id
    }
  });
  return response;
};

const deleteEcosystem = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_ECOSYSTEM,
    variables: {
      id: id
    }
  });
  return response;
};

const tokenAuth = (apollo, username, password) => {
  const response = apollo.mutate({
    mutation: TOKEN_AUTH,
    variables: {
      username: username,
      password: password
    }
  });
  return response;
};

const addDataSet = (
  apollo,
  category,
  datasourceName,
  uri,
  projectId,
  filters
) => {
  const response = apollo.mutate({
    mutation: ADD_DATASET,
    variables: {
      category: category,
      datasourceName: datasourceName,
      uri: uri,
      projectId: projectId,
      filters: JSON.stringify(filters)
    }
  });
  return response;
};

const fetchGithubOwnerRepos = (apollo, owner) => {
  const response = apollo.mutate({
    mutation: FETCH_GITHUB_OWNER_REPOS,
    variables: {
      owner: owner
    }
  });
  return response;
};

const deleteDataset = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_DATASET,
    variables: {
      id: id
    }
  });
  return response;
};

const addCredential = (apollo, datasourceName, token, name) => {
  const response = apollo.mutate({
    mutation: ADD_CREDENTIAL,
    variables: {
      datasourceName: datasourceName,
      token: token,
      name: name
    }
  });
  return response;
};

const deleteCredential = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_CREDENTIAL,
    variables: {
      id: id
    }
  });
  return response;
};

const archiveDataset = (apollo, id) => {
  const response = apollo.mutate({
    mutation: ARCHIVE_DATASET,
    variables: {
      id: id
    }
  });
  return response;
};

const unarchiveDataset = (apollo, id) => {
  const response = apollo.mutate({
    mutation: UNARCHIVE_DATASET,
    variables: {
      id: id
    }
  });
  return response;
};

export {
  addProject,
  deleteProject,
  moveProject,
  updateProject,
  addEcosystem,
  updateEcosystem,
  deleteEcosystem,
  tokenAuth,
  addDataSet,
  deleteDataset,
  fetchGithubOwnerRepos,
  addCredential,
  deleteCredential,
  archiveDataset,
  unarchiveDataset
};
